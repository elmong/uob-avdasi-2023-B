import asyncio

async def pico_w_data_task():
    while True:
        # Your Pico W data collection code here
        print("Pico is here")
        await asyncio.sleep(0.5)  # Adjust the sleep time as needed

async def main_loop():
    while True:
        print("Pygame is here")
        # Your main loop code here
        await asyncio.sleep(0.1)  # Adjust the sleep time as needed

async def main():
    pico_task = asyncio.create_task(pico_w_data_task())
    main_task = asyncio.create_task(main_loop())

    await asyncio.gather(pico_task, main_task)

if __name__ == "__main__":
    asyncio.run(main())
