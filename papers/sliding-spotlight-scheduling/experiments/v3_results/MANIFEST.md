# v3 真窗工件晋升清单（MANIFEST）

**晋升票**：票 30 (d)，2026-10-06　**晋升源**：`.scratch/sliding-spotlight-scheduling/v3-run-recheck/`（票 28 Stage 2 产物）
＋ `.scratch/sliding-spotlight-scheduling/v3-run/`（三份 brief + 功效曲线脚本）
**落点**：`papers/sliding-spotlight-scheduling/experiments/v3_results/`（caliber v3）

## 一、晋升理由

`.scratch/` 按仓库策略 gitignore，票 28 的 90 个矩阵单元 + 30 份 manifests + 标定表此前**无 tracked 落点**，`RUN_LINEAGE` 也无节点（audit4 B4）。本目录是它们唯一的可提交落点：写作期取数、真窗族 caliber 标签、`verify_v3_verdicts.py` 的复算面都指向这里。逐文件 byte 复制，md5 源/副本对账（见第三节）。

**排除**：`*.log` / `*.err` / `*.bak`（含三个 `_progress.json.bak`）不晋升 —— 日志与备份不是证据面。

## 二、各档 code head

`code_head` 取自各档 `_progress.json` 的 `code_head` 字段。**单元 pilot JSON 本身没有 git_head 字段**，head 只存在于 progress 里，故以本表为准。

| 目录 | 预算 (pop/gen) | 单元数 | `_progress.json.code_head` |
|---|---|---|---|
| `scenarios/` | — | 30 | — (scenarios 无 _progress.json；manifests 与搜索预算无关，字节由驱动器对账) |
| `matrix/` | 40/60 | 30 | `220a7961e711be09a2e32d6a17a09d4595f7782a` |
| `matrix_p80g120/` | 80/120 | 30 | `220a7961e711be09a2e32d6a17a09d4595f7782a` |
| `matrix_p160g240/` | 160/240 | 30 | `220a7961e711be09a2e32d6a17a09d4595f7782a` |

三档矩阵同 head；`220a796` = 票 28（C3/C4 参考改走 per-window r0，audit4 A1 修复），其上承 `036e297`（多窗测度缝 nextafter 修复）。`scenarios/` 是 manifests 冻结件，与搜索预算无关，故无 progress/head 字段 —— 驱动器在每档启动时对它们做字节对账。

## 三、逐文件 md5（源 = 副本）

共 126 个文件。md5 由源与副本分别计算并断言相等；下方「源 md5」与「副本 md5」两列同值即对账通过。唯一例外见第四节。

| 落点文件 | 源 md5 | 副本 md5 | 字节 | 源目录 |
|---|---|---|---|---|
| `scenarios/R1C_seed100.json` | `02590ca7e2a67b1c814b69a1af1582a7` | `02590ca7e2a67b1c814b69a1af1582a7` | 43704 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R1C_seed101.json` | `b9ac46f3a2830bd1da8cff0a11a84dbe` | `b9ac46f3a2830bd1da8cff0a11a84dbe` | 43547 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R1C_seed102.json` | `ad32f4dad7371f1458a7c333ef70c773` | `ad32f4dad7371f1458a7c333ef70c773` | 42857 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R1C_seed103.json` | `fa474ba28c4a4ebc0434825b4e29066f` | `fa474ba28c4a4ebc0434825b4e29066f` | 44593 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R1C_seed104.json` | `0c0213e0895f81d9a8c1b9be19fa697b` | `0c0213e0895f81d9a8c1b9be19fa697b` | 41026 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R1C_seed105.json` | `f8f857345d1525324019b38ab75616a8` | `f8f857345d1525324019b38ab75616a8` | 43988 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R1C_seed106.json` | `443d95e7761113aae59cbf2707723ad5` | `443d95e7761113aae59cbf2707723ad5` | 42171 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R1C_seed107.json` | `1628c71123256e4118dab5f4401e4bf9` | `1628c71123256e4118dab5f4401e4bf9` | 41928 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R1C_seed108.json` | `7102fed7ffad1c4b88982e00fffb5c8b` | `7102fed7ffad1c4b88982e00fffb5c8b` | 40772 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R1C_seed109.json` | `7d0028b36cd53a1180a18f03bd09d53a` | `7d0028b36cd53a1180a18f03bd09d53a` | 41921 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed200.json` | `13801827b9329aaf9ccbd5d34545d2ae` | `13801827b9329aaf9ccbd5d34545d2ae` | 92725 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed201.json` | `335f779a896343c63b214de16a066023` | `335f779a896343c63b214de16a066023` | 96944 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed202.json` | `2c646059f63928d06903a2781f339836` | `2c646059f63928d06903a2781f339836` | 95950 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed203.json` | `f8e8dc319f4d2c3dee7e1e80614a9ffe` | `f8e8dc319f4d2c3dee7e1e80614a9ffe` | 99040 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed204.json` | `365c74034767b6da056960fae65df635` | `365c74034767b6da056960fae65df635` | 92467 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed205.json` | `c1788f96d4ff8dfab5b9e0e907ad66a6` | `c1788f96d4ff8dfab5b9e0e907ad66a6` | 93529 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed206.json` | `25ed5c1366ded20cd412d9b4ceb178a0` | `25ed5c1366ded20cd412d9b4ceb178a0` | 97608 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed207.json` | `14ba011cbd2596fb805f330f80ba666f` | `14ba011cbd2596fb805f330f80ba666f` | 104595 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed208.json` | `caa0c5a82039a0e8b338bfa225a6f176` | `caa0c5a82039a0e8b338bfa225a6f176` | 98589 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R2F_seed209.json` | `c6aaf1cfa779dcebd4c20e26e4812744` | `c6aaf1cfa779dcebd4c20e26e4812744` | 98722 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed300.json` | `0609eb00bc3ae927a86ca1d36dd0a4d0` | `0609eb00bc3ae927a86ca1d36dd0a4d0` | 200713 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed301.json` | `19f3caf395835a3f9589c75a70ac176a` | `19f3caf395835a3f9589c75a70ac176a` | 195752 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed302.json` | `afb139e23d78037d5f5fcab65f882dc9` | `afb139e23d78037d5f5fcab65f882dc9` | 203033 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed303.json` | `c12f034d80aaa80072e4a5acc7f39afe` | `c12f034d80aaa80072e4a5acc7f39afe` | 206724 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed304.json` | `0b096a95ada372b076fd3c3256f4ce17` | `0b096a95ada372b076fd3c3256f4ce17` | 203578 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed305.json` | `4615f883a5f867cb1b1d00a469ecf007` | `4615f883a5f867cb1b1d00a469ecf007` | 201099 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed306.json` | `51edf2d8e9aad383c0f66d72f4f5f0f5` | `51edf2d8e9aad383c0f66d72f4f5f0f5` | 201962 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed307.json` | `4a3c18e633e038dc53119acdcb9879f6` | `4a3c18e633e038dc53119acdcb9879f6` | 204396 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed308.json` | `18975a390ad2b4af7945c7f87e5f68a9` | `18975a390ad2b4af7945c7f87e5f68a9` | 201836 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `scenarios/R3H_seed309.json` | `6ec9d7bb4d74290890de2c2c7dca08d5` | `6ec9d7bb4d74290890de2c2c7dca08d5` | 199328 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/scenarios/` |
| `matrix/_progress.json` | `3d770ba09e7b1f203e98209ec111bd60` | `3d770ba09e7b1f203e98209ec111bd60` | 16311 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed100.json` | `cc47f0780a087d1c47cc6bafa34efaf6` | `cc47f0780a087d1c47cc6bafa34efaf6` | 25668 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed101.json` | `4644f482840c33bc7a884fc0e37bddda` | `4644f482840c33bc7a884fc0e37bddda` | 26153 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed102.json` | `ad8ba600d8218a0d457a434e716608fa` | `ad8ba600d8218a0d457a434e716608fa` | 27802 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed103.json` | `28cedcfd9f84f140d03f62994081abab` | `28cedcfd9f84f140d03f62994081abab` | 27733 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed104.json` | `43261551ee8360c8d68a73d5aef31d38` | `43261551ee8360c8d68a73d5aef31d38` | 23278 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed105.json` | `eba8822a39010ae93f54479c4eb8e9f4` | `eba8822a39010ae93f54479c4eb8e9f4` | 20987 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed106.json` | `a372221fe39940a1ec08133f26d9a148` | `a372221fe39940a1ec08133f26d9a148` | 22459 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed107.json` | `f0bf967e68a0be0b8c7bfb8654f7c029` | `f0bf967e68a0be0b8c7bfb8654f7c029` | 26785 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed108.json` | `bb967cf063da9594e441452f867c14df` | `bb967cf063da9594e441452f867c14df` | 28262 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R1C_seed109.json` | `f838927cb9273f1050832b927c15538f` | `f838927cb9273f1050832b927c15538f` | 27011 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed200.json` | `86756869f52ab721a5c7f0ceda1312bc` | `86756869f52ab721a5c7f0ceda1312bc` | 17762 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed201.json` | `f54246524abb6b3e152924ceaf3772ee` | `f54246524abb6b3e152924ceaf3772ee` | 17197 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed202.json` | `476beceea6140fc2b6a9520382235e5c` | `476beceea6140fc2b6a9520382235e5c` | 26029 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed203.json` | `b21076a557478fe2df6b881691df88c0` | `b21076a557478fe2df6b881691df88c0` | 12755 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed204.json` | `68e266cff613680f807ee0ff0b8a1e8e` | `68e266cff613680f807ee0ff0b8a1e8e` | 36747 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed205.json` | `ab4ef74a903bdacdfd0c98ccdd85559e` | `ab4ef74a903bdacdfd0c98ccdd85559e` | 31350 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed206.json` | `c60c2c39f567a95c3a74fc09e0c416c4` | `c60c2c39f567a95c3a74fc09e0c416c4` | 46552 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed207.json` | `37b1ccc99188bc3b5439b0efcfaacb68` | `37b1ccc99188bc3b5439b0efcfaacb68` | 22539 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed208.json` | `d5c074ec9abad2349390bfddeb367036` | `d5c074ec9abad2349390bfddeb367036` | 2161 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R2F_seed209.json` | `1e857005c1462bc93cfdf8f42aff06ea` | `1e857005c1462bc93cfdf8f42aff06ea` | 13498 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed300.json` | `888775d80e57dd7d8ca15ea243c23560` | `888775d80e57dd7d8ca15ea243c23560` | 3693 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed301.json` | `97d17b4940bfd90e627956ccbfefaced` | `97d17b4940bfd90e627956ccbfefaced` | 36722 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed302.json` | `2085b6007111ebe014c8159cd4eae502` | `2085b6007111ebe014c8159cd4eae502` | 3634 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed303.json` | `8cf721c597af5b26b3fe09b5bbe376af` | `8cf721c597af5b26b3fe09b5bbe376af` | 30639 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed304.json` | `02928e5e87c8311f6a1af727dbf32b3e` | `02928e5e87c8311f6a1af727dbf32b3e` | 21045 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed305.json` | `d7e1d8a9900dab71382771d21db2e3f7` | `d7e1d8a9900dab71382771d21db2e3f7` | 3623 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed306.json` | `7c302f0ae9d6aaeb3fa537955952e7de` | `7c302f0ae9d6aaeb3fa537955952e7de` | 3614 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed307.json` | `80d22cb8b5a7df0f57cfc84cb5f2dd7a` | `80d22cb8b5a7df0f57cfc84cb5f2dd7a` | 3708 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed308.json` | `0da6247481952b6f8759e05b8dba0c33` | `0da6247481952b6f8759e05b8dba0c33` | 3547 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix/pilot_R3H_seed309.json` | `37b9ef47908df5be02f3693b79386952` | `37b9ef47908df5be02f3693b79386952` | 28413 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix/` |
| `matrix_p80g120/_progress.json` | `06f567677831b79785e28e8d2be2d5dd` | `06f567677831b79785e28e8d2be2d5dd` | 16630 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed100.json` | `f03d9cdc9a632025ebf5f3dff8da18f1` | `f03d9cdc9a632025ebf5f3dff8da18f1` | 57438 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed101.json` | `cb48ac0f1db408006c6b266b972c0587` | `cb48ac0f1db408006c6b266b972c0587` | 50435 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed102.json` | `7fd3ef739eda254b7f8cb89633285980` | `7fd3ef739eda254b7f8cb89633285980` | 50661 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed103.json` | `02066875df29fef05f8e705b5cca7899` | `02066875df29fef05f8e705b5cca7899` | 55216 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed104.json` | `4657de5ccaf0909f53b21bafe572684a` | `4657de5ccaf0909f53b21bafe572684a` | 45461 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed105.json` | `afd0c9f0d5b498e2e03f723254e437eb` | `afd0c9f0d5b498e2e03f723254e437eb` | 52106 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed106.json` | `722763fd390add2ea8940773b510b6d0` | `722763fd390add2ea8940773b510b6d0` | 52840 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed107.json` | `ce0de7e83e77533a62bbb7b8657758ae` | `ce0de7e83e77533a62bbb7b8657758ae` | 49392 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed108.json` | `76d9cbd6950e3b71f0afc6941612816d` | `76d9cbd6950e3b71f0afc6941612816d` | 48659 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R1C_seed109.json` | `36678331dde8e52c972f6a13c096a996` | `36678331dde8e52c972f6a13c096a996` | 49483 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed200.json` | `5e03d7f0d5fa1ded2a7ad6f40f1c3e5b` | `5e03d7f0d5fa1ded2a7ad6f40f1c3e5b` | 40397 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed201.json` | `ee993558b5f48ba52eba6c342221944d` | `ee993558b5f48ba52eba6c342221944d` | 73327 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed202.json` | `63e00d697a3a5272c000becf3a0d3061` | `63e00d697a3a5272c000becf3a0d3061` | 43578 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed203.json` | `3dee0ece0d34cb7b47137d3fda0cf722` | `3dee0ece0d34cb7b47137d3fda0cf722` | 75151 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed204.json` | `9c1cb10f0cf011eae4c5cb977396a4d4` | `9c1cb10f0cf011eae4c5cb977396a4d4` | 60385 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed205.json` | `466f71f981617bd8ed71c395a648c145` | `466f71f981617bd8ed71c395a648c145` | 56657 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed206.json` | `ae222244dd86b440cb3269b3397b06a5` | `ae222244dd86b440cb3269b3397b06a5` | 54496 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed207.json` | `5ba9326b4d3fa335be6fdc01181ed0be` | `5ba9326b4d3fa335be6fdc01181ed0be` | 98218 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed208.json` | `aa0e811cc9fa6ba4380d2d89e438ddbb` | `aa0e811cc9fa6ba4380d2d89e438ddbb` | 39953 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R2F_seed209.json` | `551251a9e559705792fecf5e987cc94a` | `551251a9e559705792fecf5e987cc94a` | 30573 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed300.json` | `e02ed291294375274639d251620059d0` | `e02ed291294375274639d251620059d0` | 74084 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed301.json` | `69a54533fb445b6519d39544bdd35d53` | `69a54533fb445b6519d39544bdd35d53` | 66331 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed302.json` | `263625f5cdebd56d4d76115045942d91` | `263625f5cdebd56d4d76115045942d91` | 52485 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed303.json` | `c1d07fc3339e4d46f4475f6b0ea29af4` | `c1d07fc3339e4d46f4475f6b0ea29af4` | 87095 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed304.json` | `fdea40b2abfe2989c44ea83b38d7f486` | `fdea40b2abfe2989c44ea83b38d7f486` | 74723 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed305.json` | `524c8f7b695274fa0447fa7a9c2f86e1` | `524c8f7b695274fa0447fa7a9c2f86e1` | 12984 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed306.json` | `7c366dbbaf082ade2b785bb73acc36f1` | `7c366dbbaf082ade2b785bb73acc36f1` | 54889 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed307.json` | `b00e8be94a2ae65ac1c99c7a369d7845` | `b00e8be94a2ae65ac1c99c7a369d7845` | 21866 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed308.json` | `cbaf5fa11b08282f449f534972463556` | `cbaf5fa11b08282f449f534972463556` | 84423 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p80g120/pilot_R3H_seed309.json` | `2ae99b15155cbe31f6358dac589978b1` | `2ae99b15155cbe31f6358dac589978b1` | 92614 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p80g120/` |
| `matrix_p160g240/_progress.json` | `ba348f7e66c16c78a20b82b82eaa71d6` | `ba348f7e66c16c78a20b82b82eaa71d6` | 16689 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed100.json` | `c0c0d1a4ab4e7bec113b160d1742a8a0` | `c0c0d1a4ab4e7bec113b160d1742a8a0` | 100804 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed101.json` | `1ffee5c577aeaac8705dc4151047b51c` | `1ffee5c577aeaac8705dc4151047b51c` | 96476 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed102.json` | `5afd1a6d3f7c8877d7ac46fb2a88e934` | `5afd1a6d3f7c8877d7ac46fb2a88e934` | 99038 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed103.json` | `375e7c180b8f009aa3aa211e4c5867bd` | `375e7c180b8f009aa3aa211e4c5867bd` | 107507 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed104.json` | `28a547bc97c41054941884eccc880e22` | `28a547bc97c41054941884eccc880e22` | 82806 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed105.json` | `bee5253f695ea7e84474d35879c2cf84` | `bee5253f695ea7e84474d35879c2cf84` | 96034 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed106.json` | `ab4954a2ee94ffc7e220955ac681ae45` | `ab4954a2ee94ffc7e220955ac681ae45` | 94255 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed107.json` | `db7ec3c782d01942c01c9d62dc85c132` | `db7ec3c782d01942c01c9d62dc85c132` | 89137 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed108.json` | `46b3b1d34e6e9a33cdcfb4901dc8cb25` | `46b3b1d34e6e9a33cdcfb4901dc8cb25` | 93529 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R1C_seed109.json` | `69c1b11a29a9facd5f90df3fd98a4711` | `69c1b11a29a9facd5f90df3fd98a4711` | 93055 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed200.json` | `f73a5cd7baeab180bfcca098ef684321` | `f73a5cd7baeab180bfcca098ef684321` | 89355 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed201.json` | `5bc0548b972e237767b1b349da470837` | `5bc0548b972e237767b1b349da470837` | 73555 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed202.json` | `a213bae746375c42660d610c86563506` | `a213bae746375c42660d610c86563506` | 115580 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed203.json` | `98f48749285ff44ba6985b7aae795cde` | `98f48749285ff44ba6985b7aae795cde` | 100330 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed204.json` | `f8b27c31c9689c00303364c7cd1db5bd` | `f8b27c31c9689c00303364c7cd1db5bd` | 87926 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed205.json` | `539e6ce88425954976a3bf2964af6ada` | `539e6ce88425954976a3bf2964af6ada` | 82213 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed206.json` | `412998d163096e8c00be0e2a153c634b` | `412998d163096e8c00be0e2a153c634b` | 81070 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed207.json` | `b615fe23729e691511dc3b5686e13c74` | `b615fe23729e691511dc3b5686e13c74` | 76145 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed208.json` | `2b81dc6d2b39ffa6102f091d4fba3b01` | `2b81dc6d2b39ffa6102f091d4fba3b01` | 123868 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R2F_seed209.json` | `1fbf4865a30cf4ce406efcdc5039b3a0` | `1fbf4865a30cf4ce406efcdc5039b3a0` | 80428 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed300.json` | `2403ad4516e16c7d279a8cb771dd0a79` | `2403ad4516e16c7d279a8cb771dd0a79` | 170809 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed301.json` | `332b083b77ddb79dbadc68cc1f70ba28` | `332b083b77ddb79dbadc68cc1f70ba28` | 68181 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed302.json` | `328511358a9b2edbb30aa71be4e8e17c` | `328511358a9b2edbb30aa71be4e8e17c` | 242993 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed303.json` | `a79a54e2118b20d8569c78810c19ad58` | `a79a54e2118b20d8569c78810c19ad58` | 116265 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed304.json` | `9b17505f612c2bd531c9130ccef6a5f1` | `9b17505f612c2bd531c9130ccef6a5f1` | 246995 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed305.json` | `5b0310e632ff8f9e8c6a31cb01cb2a98` | `5b0310e632ff8f9e8c6a31cb01cb2a98` | 176387 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed306.json` | `8fba510ece77e0a728fb479c0ef03294` | `8fba510ece77e0a728fb479c0ef03294` | 216169 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed307.json` | `5d00e57e9556c7e150cc3fbb5f643a22` | `5d00e57e9556c7e150cc3fbb5f643a22` | 187166 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed308.json` | `048f528907ac36df40272390ff5d9cbc` | `048f528907ac36df40272390ff5d9cbc` | 186958 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `matrix_p160g240/pilot_R3H_seed309.json` | `45efd87576ae4540267bb9ca1eac468b` | `45efd87576ae4540267bb9ca1eac468b` | 206312 | `.scratch/sliding-spotlight-scheduling/v3-run-recheck/matrix_p160g240/` |
| `LAUNCH_BRIEF.md` | `391be93659f8082026892a9200b4017e` | `391be93659f8082026892a9200b4017e` | 3151 | `.scratch/sliding-spotlight-scheduling/v3-run/` |
| `CALIBRATION_BRIEF.md` | `4817d06cf7f0309a2497f09dd0809635` | `4817d06cf7f0309a2497f09dd0809635` | 2224 | `.scratch/sliding-spotlight-scheduling/v3-run/` |
| `_power_curve_rq_effect_size.py` | `356e90b921cfbf06292aefa7536f25bc` | `356e90b921cfbf06292aefa7536f25bc` | 1197 | `.scratch/sliding-spotlight-scheduling/v3-run/` |

## 四、例外：`CALIBRATION_PREREG.md`（唯一被改动的晋升副本）

**理由**：晋升后该文件进入 `check_red_lines.py` 的扫描面（门禁只豁免路径组件恰为 `results` 的目录，`v3_results` 不豁免），而其第 3 行含「前沿塌缩」一词且**原句无证伪语境**，会被判为 R2 违规（本清单写下时该门禁即报此 1 条）。该词所指的现象已由该文件自身的判定表判为搜索伪影、塌缩叙事作废，故此处引用它是复述已判伪影的词，不是断言物理塌缩。票面为此设例外条款。

**处置**：只在第 3 行末尾**插入**一句注记（同句含已证伪语境词「伪影」「作废」，过 R2 上下文分类）；**判词表与全部数值零改动**，其余各行字节不变。

- 源 md5（`.scratch/.../v3-run/CALIBRATION_PREREG.md`，**未被改动**）：`2fb8b1c88a01bbc6792946e685f6a5cc`
- 副本 md5（`experiments/v3_results/CALIBRATION_PREREG.md`，仅第 3 行加注）：`29aed2d2bca46d9c8d16721009b5b888`
- 插入的句子：

  > 【晋升副本注记（T30 例外条款）】该现象的物理性未定，后经本预注册的判定表判为搜索伪影（SEARCH-ARTIFACT，塌缩叙事作废）；本预注册即为判定其是否属搜索伪影而设，判词与数值零改动。

**注记为真**：该判定表（同一文件第五节执行记录）实测 R2F = SEARCH-ARTIFACT、R3H = SEARCH-ARTIFACT，故「判为搜索伪影」是本仓库已判定的结论，非事后追认。**注记只加上下文，原句一字未删**；其余 126 个晋升副本与源 md5 逐位一致。

**第二次例外追加（票 36 / review-fable A1，2026-10-06）**：该副本的 md5 因下述勘误注记**再次变化**，
本节记录随之更新，例外**理由与处置口径不变**（仍是「只加注记、判词表与数值零改动」）：

- 现行副本 md5：`6b1576248711015b77c07fff59899ac1`（前值 `29aed2d2bca46d9c8d16721009b5b888`）
- 源 md5 **不变**：`.scratch/.../v3-run/CALIBRATION_PREREG.md` = `2fb8b1c88a01bbc6792946e685f6a5cc`
  （票 36 未触碰 scratch 源件；注记只加在晋升副本上）
- 新增注记：`CALIBRATION_PREREG.md` 第 56 行后的 **【勘误注记（T36 / review-fable A1）】** 块——
  更正「值域 31–111」为**单任务单元**（`pilot_R3H_seed300.json`）被误升族级，登记**逐族实测族域**
  R1C [1.35, 2.04] / R2F [55.05, 135.22] / R3H [29.75, 123.70]（90 单元 pooled，cv ≤ 1e-9）。
- **判词表、MDE₈₀、功效、预算结论一律零改动**；`scripts/verify_v3_verdicts.py` 仍 33 checks rc=0。
- 机器校验不受影响：该文件**按设计**不在 §三 的同 md5 表格内（票 30 例外条款），
  故 `_t30_manifest_verify.py` 的表格重算不覆盖它；本节散文记录是它唯一的 md5 登记处。

> 3 行走查（票面例外条款原文）：「该现象物理性未定，本预注册即为判定其是否搜索伪影而设」类注记 —— 同句一并点明该词已判为搜索伪影，故红线的上下文分类判其为「报告已证伪结论」而非断言。**不许删事实过门禁**：要过线只能给该行补真实的证伪或禁止语境（如本目录「已判为搜索伪影」或「禁止再宣称」），不能抽掉事实本身。

## 五、机器锚

`scripts/verify_v3_verdicts.py` 从本目录复算并断言全部判词读数（R_fam / R2F-R3H 基值与上确界 / promotion 90 单元 / 前沿与 distinct-fq / R1C anchor 与前沿区间 / MDE / δ=6.0 / 功效），rc=0 为通过。
