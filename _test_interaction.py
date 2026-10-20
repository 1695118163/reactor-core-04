import os
import asyncio, sys
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8778/"
OUT = os.path.dirname(os.path.abspath(__file__))

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1100, "height": 640})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append("PAGEERROR: " + str(e)))

        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(3500)

        # A：初始
        await page.screenshot(path=OUT + r"\ia.png")

        # B：裸移鼠标（不按键）—— 视角必须不变
        await page.mouse.move(300, 300)
        await page.wait_for_timeout(400)
        await page.mouse.move(850, 500, steps=25)
        await page.wait_for_timeout(900)
        await page.screenshot(path=OUT + r"\ib.png")

        # C：右键按住拖拽 —— 视角必须转
        await page.mouse.move(700, 380)
        await page.mouse.down(button="right")
        await page.mouse.move(300, 300, steps=30)
        await page.mouse.up(button="right")
        await page.wait_for_timeout(1200)
        await page.screenshot(path=OUT + r"\ic.png")

        # D：左键点核心 —— 触发脉冲
        await page.mouse.click(550, 330)
        await page.wait_for_timeout(250)
        await page.screenshot(path=OUT + r"\id.png")

        # E：空格 SCRAM
        await page.keyboard.press("Space")
        await page.wait_for_timeout(2600)
        state = await page.eval_on_selector("#v-state", "el => el.textContent")
        await page.screenshot(path=OUT + r"\ie.png")

        print("STATE_AFTER_SCRAM:", state)
        print("CONSOLE_ERRORS:", errors[:6] if errors else "none")
        await browser.close()

asyncio.run(main())
