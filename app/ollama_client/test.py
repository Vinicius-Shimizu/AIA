from model import Model
import asyncio


async def main():
    model = await Model.create(mcp_server_url="http://localhost:8080/mcp")
    user_message = "Quais ferramentas voce tem?"
    response = await model.handleQuery(query=user_message)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())