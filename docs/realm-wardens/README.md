# Realm Wardens 素材生产（TapTap Maker）

来源需求：`Realm Wardens — remodel and art prompts`（外部生成器提示词清单，90 个 3D 资产 + 19 张 2D 美术）。
本目录把这份清单变成**可复跑的 Maker 生成流水线**，产物直接落到本项目 `assets/image`、`assets/model`。

## 目录

| 文件 | 作用 |
|---|---|
| `manifest.json` | 由 `tools/realm_wardens_manifest.py` 生成的机器可读清单：90 个资产（id / 分组 / 英文提示词 / 主体类型 / 质量档 / 面数上限 / 目标尺寸 / 动画部件名）+ 19 张 2D 美术 |
| `state.json` | 逐资产状态账本：概念图路径、3D `asset_id`、任务状态、交付后的模型路径 |
| `run.log` | 每次运行的时间戳日志 |
| `sheet_<group>.png` | 概念图拼版，按分组快速验收（`tools/realm_wardens_sheet.py`） |
| `index.md` | 资产 id → 本地文件路径对照表 |

## 生成链路

1. **概念图**：`generate_image` / `batch_generate_images`，1:1、1024x1024，提示词 = 原 prompt + `style_block`，命名 `rw_<id>_concept`。
2. **3D**：`create_3d_asset`，`generation_strategy=direct`，以概念图作为 front 图做图生模（`image_to_model`）；
   质量档按分组：boss / 重装角色 `high_quality`，普通单位 `balanced`，地图小道具 `fast`；
   面数上限按原文档：角色/塔 6000、boss 15000、道具 1500。
3. **2D 美术**：`generate_image`，key art 1920x1080、logo 1600x600 透明、地图卡 800x450、成就徽章 256x256 透明。

## 命令

```bash
python3 tools/realm_wardens_manifest.py          # 重建清单
python3 tools/realm_wardens_gen.py concepts      # 只跑概念图（可按 --groups 过滤）
python3 tools/realm_wardens_gen.py models --parallel 4
python3 tools/realm_wardens_gen.py art
python3 tools/realm_wardens_gen.py status
python3 tools/realm_wardens_sheet.py             # 重生成拼版
bash tools/realm_wardens_all.sh                  # 全量串行（后台 nohup 用）
```

驱动脚本直接连 Maker 插件随附的官方 runtime（`vendor/taptap-maker/dist/maker.js`），复用同一
`~/.taptap-maker` 凭证与项目绑定，因此可以无人值守批量跑；`state.json` 让中断后重跑时跳过已完成项。

## 本次运行结果（2026-11-24 19:38–21:05）

| 项目 | 数量 | 落地位置 |
|---|---|---|
| 概念图 | 90 / 90 | `assets/image/rw_<id>_concept_*.png`（1024×1024） |
| 3D 资产 | 90 / 90 | `assets/model/<asset_id>/`（UMD2 mdl + Materials + Textures + Prefabs） |
| 2D 美术 | 19 / 19 | `assets/image/rw_key_art|logo|map_*|badge_*` |

- 3D 总体积约 327 MB（mdl 122 MB + 贴图 114 MB），单个 3–4 MB；后续要考虑构建体积时做 `retopology` 或贴图降级。
- 角色全部按静态模型交付，未执行 `rig`；需要动作时对单个资产调用 `post_process: rig`。
- 登录/授权：必须用插件随附 runtime（`vendor/taptap-maker/dist/maker.js`），旧 `~/.taptap-maker/mcp-runtime/0.0.32` 会报凭证失效。

## 与原始文档规格的差异（重要）

原文第 7 节要求的是一套 Blender 后处理（顶点色、部件拆分、GLB 单根节点）。Maker 交付的是 UrhoX 资产包，差异如下：

| 原规格 | Maker 实际交付 |
|---|---|
| 单 GLB、`public/models/models.glb` | 每资产一个目录 `assets/model/<asset_id>/`（`.mdl` + Materials + Textures + Prefabs） |
| 顶点色、无贴图 | PBR 贴图（1K 级），材质 XML 正常可用于 UrhoX |
| 动画部件 `ArmR__archer` 等拆分 | 单一融合网格，**未拆分部件**；需要代码驱动摆动时得另行拆分或改用骨骼 |
| A-pose / 脚底在 y=0 / 面向 +Z | 图生模的自然站立姿态，未做统一朝向与轴心校正 |
| 三角形预算硬约束 | 通过 `face_limit` 请求，服务端会按质量档裁剪，未逐资产核验 |

所以：**本批产物可直接用在 Maker/UrhoX 里做显示与摆放**；若要严格复用原 Web 游戏的加载器（顶点色 + 部件旋转），还需一轮建模/Blender 后处理，或用 `create_3d_asset` 的 `post_process` 做 `retopology` / `rig`。

骨骼：本批全部按“静态模型”交付，没有做 `rig`。需要动作的角色后续可对单个资产调用
`post_process: rig`，再在引擎里播动画。
