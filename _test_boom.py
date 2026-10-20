import os
import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8778/"
OUT = os.path.dirname(os.path.abspath(__file__))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        page = await b.new_page(viewport={"width": 1280, "height": 720})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(2500)

        # 触发切尔诺贝利
        await page.evaluate("__sim.temp = 0.9; __sim.power = 0.95; __sim.target = 1.05")
        await page.keyboard.press("Space")

        # 1.55s 后爆炸 —— 抓爆点
        await page.wait_for_timeout(1620)
        await page.screenshot(path=OUT + r"\boom1.png")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT + r"\boom2.png")

        st = await page.evaluate("({dead: __sim.dead, debris: __state.mode})")
        print("爆炸后:", st)

        # 熔毁后控制是否失效
        before = await page.evaluate("({t: __sim.target, c: __sim.coolant})")
        box = await page.locator("#track").bounding_box()
        await page.mouse.move(box["x"] + box["width"] * 0.3, box["y"] + box["height"] / 2)
        await page.mouse.down(); await page.mouse.up()
        await page.keyboard.press("c")
        await page.keyboard.press("Space")
        await page.wait_for_timeout(600)
        after = await page.evaluate("({t: __sim.target, c: __sim.coolant, mode: __state.mode})")
        print("熔毁后尝试操作:", before, "->", after)

        print("errors:", errs[:3] if errs else "none")
        await b.close()

asyncio.run(main())
