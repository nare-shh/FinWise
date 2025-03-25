from groq import Groq
from dotenv import load_dotenv
load_dotenv()



client = Groq()

chat_completion = client.chat.completions.create(
    #
    #
    messages=[


        {
            "role": "system",
            "content": "you are a helpful assistant."
        },
        {
            "role": "user",
            "content": "hi",
        }
    ],

    model="llama-3.3-70b-versatile",


    temperature=0.5,

    top_p=1,


    stop=None,

    stream=False,
)

print(chat_completion.choices[0].message.content)