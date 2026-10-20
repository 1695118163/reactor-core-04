import os
import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8778/"
OUT = os.path.dirname(os.path.abspath(__file__))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        page = await b.new_page(viewport={"width": 1100, "height": 640})
        errs = []
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))

        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        c0 = await page.evaluate("window.__cam()")
        # 停掉自动漂移的影响：记下时间点，短窗口内比较
        await page.mouse.move(200, 200)
        await page.wait_for_timeout(120)
        a1 = await page.evaluate("window.__cam()")
        await page.mouse.move(900, 520, steps=30)     # 裸移鼠标，不按键
        await page.wait_for_timeout(600)
        a2 = await page.evaluate("window.__cam()")

        # 右键拖拽
        await page.mouse.move(700, 340)
        await page.mouse.down(button="right")
        await page.mouse.move(320, 300, steps=30)
        await page.mouse.up(button="right")
        await page.wait_for_timeout(500)
        a3 = await page.evaluate("window.__cam()")

        # 悬停到核心上，看 hover 是否被识别
        await page.mouse.move(550, 330)
        await page.wait_for_timeout(300)
        hover = await page.evaluate("window.__cam()")

        print(f"init          yaw={c0['yaw']:.4f} pitch={c0['pitch']:.4f} dist={c0['dist']:.2f}")
        print(f"before move   yaw={a1['yaw']:.4f} pitch={a1['pitch']:.4f}")
        print(f"after bare    yaw={a2['yaw']:.4f} pitch={a2['pitch']:.4f}   dx={abs(a2['yaw']-a1['yaw']):.4f}")
        print(f"after rdrag   yaw={a3['yaw']:.4f} pitch={a3['pitch']:.4f}   dx={abs(a3['yaw']-a2['yaw']):.4f}")
        print("hover pick:", hover["hovered"])
        print("errors:", errs[:4] if errs else "none")

        # 右键拖拽后截图
        await page.screenshot(path=OUT + r"\ib_after_rdrag.png")
        await b.close()

asyncio.run(main())
