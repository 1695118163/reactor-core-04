# 反应堆 · 核心 04

一座能把你炸死的压力水冷反应堆。幽蓝的切伦科夫光从压力容器里透出来，外面是金属环带、六根可插拔的控制棒、四条立式冷却管、两根会垂会晃的软管，还有一块功率滑条。

全部由代码生成——没有贴图、没有模型、没有 HDR。

## 跑起来

```bat
start.bat
```

起 `python -m http.server 8778` 然后用 Chrome 打开 <http://127.0.0.1:8778/>。

> 必须走 http。ES Module + importmap 在 `file://` 下会被 CORS 挡掉。

## 玩法

左下角是控制面板：**拖动滑条**设定目标功率。

| 档位 | 范围 | 行为 |
| --- | --- | --- |
| 低功率 | 0–30% | 温度会掉到很低，画面发暗 |
| 正常功率 | 30–70% | 稳态，温度稳在 40% 上下 |
| 高功率 | 70–92% | 温度缓慢爬升到 ~77%，能一直运行 |
| 极限功率 | 92–101% | 温度逼近临界，随时可能越线 |
| 超临界 | >101% | 必炸，只是时间问题 |

温度不是摆设：过了 80% 屏幕边缘开始闪红，核心从幽蓝转向白热再转向橙红，泛光和色差一起拉满。

**按 C 注水**：3 次配额，每次 3.4 秒强冷却，用完每 11 秒补一次。注水的瞬间两根软管会被水锤顶得抖一下。

**切尔诺贝利**：温度 > 70% 且功率 > 78% 的时候按空格插棒 —— 石墨头置换空泡，功率正反馈，1.5 秒后整台机子炸掉。这是 RBMK 的真实死法，不是随便写的。

**熔毁之后**按 R 重启。

## 声音（真素材，不是合成）

`vendor/sfx/` 里是 5 个从 **OpenGameArt** 下载的真实录音，没有一个是代码生成的：

| 文件 | 用途 | 来源 |
| --- | --- | --- |
| `hum.ogg` | 机房低频轰鸣，常驻，音量跟功率走 | [Engine Sound](https://opengameart.org/content/engine-sound) |
| `alarm.ogg` | 温度 > 80% 时循环的警报 | [Short Alarm](https://opengameart.org/content/short-alarm) |
| `siren.mp3` | 熔毁后的长鸣 | [Sirens And Alarm Noise](https://opengameart.org/content/sirens-and-alarm-noise) |
| `explosion.mp3` | 爆炸那一下 | [Big Explosion](https://opengameart.org/content/big-explosion) |
| `drone.ogg` | 备用环境层 | [Sci-Fi Drone Loop](https://opengameart.org/content/sci-fi-drone-loop) |

浏览器不允许自动播放，所以第一次点击或按键时才解锁 AudioContext。按 M 静音。

## 碎屑：能，而且做了

爆炸瞬间生成 260 块碎片（`InstancedMesh`，一次 draw call），每块有自己的位置、速度、角速度：

```js
d.v.y -= 15 * dt;                 // 重力
d.p.addScaledVector(d.v, dt);
if (d.p.y < -3.55) {              // 落地反弹
  d.v.y *= -0.30; d.v.x *= 0.62; d.v.z *= 0.62;
  d.rv.multiplyScalar(0.55);
}
```

配合火球（Sprite 从 2.2 膨胀到 19 并淡出）、地面冲击波、壳体消失。炸完之后所有控件失效——滑条不动、注水按钮死、空格无效、点控制棒只回一句"堆芯已熔毁"。


## 软体：为什么管子能软

能。用的是最经典的 **Verlet 质点链 + 距离约束**：

```js
// 积分：位置 + (位置 - 上一帧位置) * 阻尼 + 重力
p.x += (p.x - q.x) * damp;
p.y += (p.y - q.y) * damp + g;

// 约束：迭代 5 次，把每段拉回固定长度
const diff = ((d - HOSE_SEG) / d) * 0.5;
a += dir * diff;  b -= dir * diff;

// 地面碰撞 + 侧向摩擦
if (p.y < GROUND) { p.y = GROUND; q.x += (p.x - q.x) * 0.55; }
```

首端硬固定在接口上，末端软锚在地面（受冲击会被拖走一段再拉回来）。整条链每帧当成样条，重新生成一次 `TubeGeometry` 的顶点。

所以：静止时会自己垂成悬链线，注水时被顶得抖，爆炸时被冲击波甩开。

**同样的手法也用在控制棒的线缆上** —— 之前线缆是静态几何，棒一升降线缆就悬空断开。现在每帧按棒的当前高度重算曲线顶点，棒插到底线缆就跟着缩下去。

## 场景构成

| 部件 | 做法 |
| --- | --- |
| 深空穹顶 | 半径 150 的 BackSide 球，三段渐变 + 极淡星云 |
| 环境贴图 | `PMREMGenerator.fromScene()` 现场烘：细长冷白灯条 + 竖直侧光 |
| 压力容器外壳 | 菲涅尔 + 扫描带 + 经纬网 + 锐利环境高光 |
| 等离子内核 | 三层驻波对流；`uHeat` 控制从幽蓝到橙红的黑体过渡 |
| 炽白核心 | 两层 Sprite + 9,000 个 GPU 粒子 |
| 切伦科夫辐射 | 1,000 条 LineSegments，相位独立闪烁 |
| 体积光柱 | 开口圆柱 + 侧面 fresnel + 流动条纹 |
| 光内浮尘 | 1,100 点，只在光柱里亮 |
| 金属结构 | 96 颗法兰螺栓（InstancedMesh）、16 个加固环、12 个执行器 |
| **落地基座** | 环形底座 + 8 根斜撑 + 4 条立式冷却管 |
| **柔性软管 ×2** | Verlet 质点链，34 节，每帧重建管体 |
| 悬浮仪表屏 | 两块 CanvasTexture，8Hz 重画波形 |
| 后处理 | Bloom → 色差/颗粒/暗角 → OutputPass |

## 修掉与推翻的

**① 线缆悬空（你截图指出的那个）**
线缆原先是一次性 `TubeGeometry` 加进 `rig`，和控制棒没有任何绑定。棒一升降就与线缆断开。改成每帧按 `rod.holder.position.y` 重算曲线、写回顶点。

**①-b 管道差一点点没接上**
四条立管末端原先固定写在 `r = 2.62`，但球壳在 `y = -1.60` 处的截面半径是 `sqrt(2.62² - 1.60²) = 2.07` —— 所以管口悬在壳外 0.55。改成按球面解算 `r`，再加一个沿法线插入的接管嘴。软管起点也从悬空改成接到立管的三通接头上。

**② 两根弧形冷却管"像口罩"**
删了。换成落地结构：环形基座 + 8 根斜撑从基座撑到赤道环 + 4 条立式冷却管从基座垂直上来弯进球体下部。装置从"漂着的球"变成"立着的机器"。

**③ 真反射地面（试过，退回来了）**
`Reflector.js` 接上以后地面出现完整的镜像球，像第二座反应堆漂在湖面上，气质完全不对。遮罩层也没能盖住底部倒影。退回暗地板 + 手绘径向光斑。

**④ 云粒子 shader 编译失败（静默）**
GLSL 里写了 JS 常量 `CORE_R`，整个 Points 一个都不渲染，控制台只有一行 `Shader Error`。

## 数值怎么定的

```js
heatIn  = power * (0.35 + power * 0.20)   // 超过 1.0 再加 (power-1)*1.6
coolOut = 0.09 + temp * 0.60 + rodCool + (注水 ? 0.55 : 0)
```

散热随温度线性增大，所以系统永远会找到平衡点：

- 65% → 平衡 37%（凉）
- 100% → 平衡 77%（稳）
- 105% → 平衡 90%（危险）
- 110% → 平衡 >100%（炸）

这是试出来的：一开始用 `power²` 做产热，结果 65% 就爆，100% 却稳不住。改成线性+小幅二次之后才有"四档"的手感差异。

## 验证

```powershell
python _test_gameplay.py   # 滑条 / 注水 / 切尔诺贝利 / 熔毁 / 重启
python _test_orbit.py      # 相机：裸移不动、右键才转
```

`_test_gameplay.py` 实际输出：

```
拖到极限: 1.089 超临界
拖回中段: 0.55 正常功率
注水后: {c: 2, t: 3.25}
插棒瞬间: {spike: 0.99, mode: 'scramming', dead: False}
1.5s 后: {dead: True, mode: 'exploded'}
重启: {dead: False, mode: 'online', temp: 0.397}
errors: none
```

## 文件

```
reactor/
├─ index.html            单文件，约 2400 行
├─ index-v1.html         最早那版存档
├─ vendor/               three r0.169.0 + jsm 后处理链
├─ _test_gameplay.py     玩法验证
├─ _test_orbit.py        相机验证
├─ _test_sequence.py     启堆序列验证
├─ final.png
└─ start.bat
```
