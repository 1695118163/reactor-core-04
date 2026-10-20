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
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))

        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(2500)

        # 1) 拖功率条
        box = await page.locator("#track").bounding_box()
        await page.mouse.move(box["x"] + box["width"] * 0.99, box["y"] + box["height"] / 2)
        await page.mouse.down(); await page.mouse.up()
        await page.wait_for_timeout(250)
        print("拖到极限:", await page.evaluate("__sim.target"),
              await page.eval_on_selector("#tierName", "el => el.textContent"))

        await page.mouse.move(box["x"] + box["width"] * 0.5, box["y"] + box["height"] / 2)
        await page.mouse.down(); await page.mouse.up()
        await page.wait_for_timeout(250)
        print("拖回中段:", await page.evaluate("__sim.target"),
              await page.eval_on_selector("#tierName", "el => el.textContent"))

        # 2) 注水
        await page.keyboard.press("c")
        await page.wait_for_timeout(250)
        print("注水后:", await page.evaluate("({c: __sim.coolant, t: __sim.coolT})"))

        # 3) 切尔诺贝利：高温 + 高功率时插棒
        await page.evaluate("__sim.temp = 0.88; __sim.power = 0.95; __sim.target = 1.05")
        await page.keyboard.press("Space")
        await page.wait_for_timeout(600)
        mid = await page.evaluate("({spike: __sim.spike, mode: __state.mode, dead: __sim.dead})")
        print("插棒瞬间:", mid)

        await page.wait_for_timeout(2200)
        after = await page.evaluate("({dead: __sim.dead, mode: __state.mode})")
        print("1.5s 后:", after)
        await page.screenshot(path=OUT + r"\p_melt.png")

        # 4) R 重启
        await page.keyboard.press("r")
        await page.wait_for_timeout(900)
        print("重启:", await page.evaluate("({dead: __sim.dead, mode: __state.mode, temp: __sim.temp})"))

        print("errors:", errs[:4] if errs else "none")
        await b.close()

asyncio.run(main())
