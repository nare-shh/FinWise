# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
import logging
import json
import sys

# Load environment variables
load_dotenv()
GROQ_API_KEY = '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'

# Configuration
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Indian Tax Assistant API",
    description="API for tax optimization, tax queries, and return filing under Indian tax system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize Groq client with error handling
try:
    client = Groq(
        api_key=GROQ_API_KEY,
    )
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    client = None

# Models for tax optimization endpoint
class Income(BaseModel):
    salary: float = Field(..., description="Annual salary income")
    house_property: float = Field(0, description="Income from house property")
    capital_gains: Dict[str, float] = Field(default_factory=dict, description="Capital gains (short_term, long_term)")
    business: float = Field(0, description="Business income")
    other_sources: float = Field(0, description="Income from other sources")

class Deduction(BaseModel):
    section_80c: float = Field(0, description="Deductions under Section 80C (max 150,000)")
    section_80d: float = Field(0, description="Deductions for medical insurance under Section 80D")
    section_80g: float = Field(0, description="Donations under Section 80G")
    nps: float = Field(0, description="NPS contributions under Section 80CCD(1B) (max 50,000)")
    hra: Optional[Dict[str, Any]] = Field(None, description="House Rent Allowance details")
    other: Dict[str, float] = Field(default_factory=dict, description="Other deductions")

class TaxOptimizationRequest(BaseModel):
    financial_year: str = Field(..., description="Financial year in YYYY-YY format")
    age: int = Field(..., description="Age of the taxpayer")
    income: Income
    deductions: Optional[Deduction] = None
    compare_regimes: bool = Field(True, description="Compare old vs new tax regime")

# Model for tax query endpoint
class TaxQueryRequest(BaseModel):
    query: str = Field(..., description="Legal tax query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")
    financial_year: Optional[str] = Field(None, description="Relevant financial year")

# Models for tax return filing endpoint
class PersonalInfo(BaseModel):
    name: str
    pan: str = Field(..., description="Permanent Account Number")
    dob: str = Field(..., description="Date of Birth (YYYY-MM-DD)")
    aadhaar: str = Field(..., description="Aadhaar number")
    email: str
    phone: str

class BankDetail(BaseModel):
    account_number: str
    ifsc_code: str
    bank_name: str
    account_type: str

class IncomeDetails(BaseModel):
    form16: Optional[Dict[str, Any]] = None
    other_income: Optional[Dict[str, Any]] = None
    tds: Optional[List[Dict[str, Any]]] = None

class TaxReturnRequest(BaseModel):
    assessment_year: str = Field(..., description="Assessment year in YYYY-YY format")
    personal_info: PersonalInfo
    bank_details: BankDetail
    income_details: IncomeDetails
    deductions: Optional[Deduction] = None
    tax_regime: str = Field("new", description="Tax regime preference ('old' or 'new')")

# Helper function to make Groq API calls with improved error handling
def get_groq_response(prompt, system_prompt=None):
    if system_prompt is None:
        system_prompt = "You are a helpful tax assistant specializing in Indian tax laws and regulations."
    
    try:
        if client is None:
            logger.error("Groq client is not initialized")
            return "Our tax assistant is currently unavailable. Please try again later."
            
        logger.info("Sending request to Groq API")
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1000
        )
        logger.info("Successfully received response from Groq API")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again in a few moments."

# Endpoint 1: Tax Optimization
@app.post("/tax-optimization")
async def tax_optimization(request: TaxOptimizationRequest):
    """
    Optimize tax calculation based on income and available deductions.
    Compares old vs new tax regime if requested.
    """
    try:
        logger.info(f"Tax optimization request received for FY {request.financial_year}")
        
        # Create a detailed prompt for the tax optimization
        prompt = f"""
        Provide tax optimization advice and calculations for an Indian taxpayer with the following details:
        - Financial Year: {request.financial_year}
        - Age: {request.age}
        
        Income Details:
        - Salary: ₹{request.income.salary}
        - House Property: ₹{request.income.house_property}
        - Capital Gains: {request.income.capital_gains}
        - Business Income: ₹{request.income.business}
        - Other Sources: ₹{request.income.other_sources}
        
        Deductions:
        {request.deductions.dict() if request.deductions else "No deductions provided"}
        
        I need you to:
        1. Calculate tax liability under the new tax regime (Budget 2023-24)
        2. {'Calculate tax under the old regime and compare both options' if request.compare_regimes else 'Focus only on the new tax regime'}
        3. Suggest 3-5 specific optimization strategies to reduce tax liability for this person
        4. Provide a clear breakdown of tax calculations
        5. Highlight any tax-saving investments they should consider before the financial year ends
        """
        
        system_prompt = """
        You are an expert Indian tax consultant specializing in personal income tax. 
        Give accurate tax calculations and optimization strategies based on the latest Indian income tax laws.
        Focus on the new tax regime introduced in Budget 2023-24, which has become the default regime.
        Your advice should:
        1. Be concise and easy to understand
        2. Provide specific numbers and calculations
        3. Focus on legitimate tax planning strategies
        4. Highlight the impact of each suggestion in rupee amounts
        5. Explain which tax regime would be better for the taxpayer and why
        """
        
        # Get response from Groq
        optimization_result = get_groq_response(prompt, system_prompt)
        
        if not optimization_result:
            raise HTTPException(
                status_code=503,
                detail="Tax optimization service is temporarily unavailable. Please try again in a few moments."
            )
        
        return {
            "tax_year": request.financial_year,
            "timestamp": datetime.now().isoformat(),
            "optimization_result": optimization_result,
            "tax_regimes_compared": request.compare_regimes
        }
    except HTTPException as he:
        logger.error(f"HTTP Exception in tax optimization: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error processing tax optimization: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your tax optimization request. Please try again."
        )

# Endpoint 2: Tax Query Bot
@app.post("/tax-query")
async def tax_query(request: TaxQueryRequest):
    """
    Provide answers to general legal tax queries related to Indian taxation.
    """
    if not client:
        raise HTTPException(status_code=503, detail="AI service is currently unavailable")
    
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
            
        logger.info(f"Tax query received: {request.query[:50]}...")
        
        # Create context-aware prompt for the tax query
        financial_year = request.financial_year or "2023-24"
        context = request.context or {}
        
        prompt = f"""
        Answer this tax query about Indian taxation:
        "{request.query}"
        
        Financial Year: {financial_year}
        
        Additional Context:
        {context}
        
        I need a clear, legally accurate answer that:
        1. Directly addresses the specific question asked
        2. References relevant sections of Income Tax Act or rules
        3. Explains how this applies specifically in the new tax regime
        4. Provides practical, actionable advice
        5. Highlights any recent changes or updates relevant to this query
        """
        
        system_prompt = """
        You are a legal tax expert specializing in Indian taxation laws. 
        Your answers should be:
        1. Accurate according to the latest Indian tax laws
        2. Clear and easy to understand while being technically correct
        3. Practical and actionable
        4. Specifically focused on the Indian tax system context
        5. Careful to cite specific tax code sections, CBDT circulars, or notifications when relevant
        
        If there's ambiguity in the query, address the most likely interpretation but acknowledge other possibilities.
        Focus on both old and new tax regimes, but emphasize the new tax regime when relevant.
        """
        
        # Get response from Groq
        query_response = get_groq_response(prompt, system_prompt)
        
        if not query_response:
            raise HTTPException(
                status_code=503,
                detail="Tax assistant service is temporarily unavailable. Please try again in a few moments."
            )
            
        return {
            "status": "success",
            "query": request.query,
            "financial_year": financial_year,
            "response": query_response,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This information is for general guidance only and should not be considered as legal tax advice."
        }
    except HTTPException as he:
        logger.error(f"HTTP Exception in tax query: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error processing tax query: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your tax query. Please try again."
        )

# Endpoint 3: Return Filing
@app.post("/return-filing")
async def return_filing(request: TaxReturnRequest):
    """
    Process tax return filing details and provide guidance on ITR filing.
    """
    logger.info(f"Return filing guidance requested for {request.assessment_year}")
    
    # Create detailed prompt for return filing guidance
    prompt = f"""
    Provide step-by-step guidance for filing income tax return in India with these details:
    
    Assessment Year: {request.assessment_year}
    Tax Regime Selected: {request.tax_regime}
    
    Income sources include:
    - Form 16 salary income: {"Yes" if request.income_details.form16 else "No"}
    - Other income sources: {"Yes" if request.income_details.other_income else "No"}
    - TDS details provided: {"Yes" if request.income_details.tds else "No"}
    
    I need:
    1. The specific ITR form this person should use
    2. A complete checklist of documents needed
    3. Step-by-step instructions for filing this return
    4. Common mistakes to avoid
    5. Key deadlines and penalties for missing them
    6. Any specific deductions or exemptions this person should claim
    7. Guidance on verification and post-filing steps
    """
    
    system_prompt = """
    You are an Indian tax filing expert with deep knowledge of the income tax return filing process. 
    Your guidance should be:
    1. Specific to the assessment year mentioned
    2. Tailored to the tax regime selected (old or new)
    3. Practical and step-by-step
    4. Focused on compliance requirements and documentation
    5. Clear about which ITR form is appropriate based on income sources
    
    Emphasize the importance of accurate reporting, proper documentation, and meeting deadlines.
    Include guidance on using the official income tax portal effectively.
    """
    
    # Get response from Groq
    filing_guidance = get_groq_response(prompt, system_prompt)
    
    # Determine ITR form based on income sources (simplified logic)
    itr_form = "ITR-1"  # Default for simplicity
    if request.income_details.other_income and "business_income" in request.income_details.other_income:
        itr_form = "ITR-3"
    elif request.income_details.other_income and "capital_gains" in request.income_details.other_income:
        itr_form = "ITR-2"
    
    return {
        "assessment_year": request.assessment_year,
        "itr_form_suggested": itr_form,
        "tax_regime": request.tax_regime,
        "filing_guidance": filing_guidance,
        "due_date": "July 31, 2023" if request.assessment_year == "2023-24" else "Standard due date: July 31",
        "timestamp": datetime.now().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "api": "Indian Tax Assistant API",
        "version": "1.0.0",
        "endpoints": [
            "/tax-optimization",
            "/tax-query",
            "/return-filing"
        ],
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)