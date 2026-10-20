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
        await page.wait_for_timeout(3000)

        await page.keyboard.press("Space")          # 停堆
        await page.wait_for_timeout(3200)
        s1 = await page.eval_on_selector("#v-state", "el => el.textContent")
        await page.screenshot(path=OUT + r"\seq1_scrammed.png")

        await page.keyboard.press("Space")          # 启堆
        await page.wait_for_timeout(4200)
        s2 = await page.eval_on_selector("#v-state", "el => el.textContent")
        p2 = await page.eval_on_selector("#v-out", "el => el.textContent")
        await page.screenshot(path=OUT + r"\seq2_starting.png")

        await page.wait_for_timeout(5200)
        s3 = await page.eval_on_selector("#v-state", "el => el.textContent")
        p3 = await page.eval_on_selector("#v-out", "el => el.textContent")

        await page.keyboard.press("h")
        await page.wait_for_timeout(500)
        help_on = await page.eval_on_selector("#help", "el => el.classList.contains('on')")
        await page.screenshot(path=OUT + r"\seq3_help.png")

        print("停堆后状态:", s1)
        print("启堆中状态:", s2, "功率:", p2)
        print("启堆完成状态:", s3, "功率:", p3)
        print("说明面板打开:", help_on)
        print("errors:", errs[:3] if errs else "none")
        await b.close()

asyncio.run(main())
