<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/finegrain-ai/refiners/main/assets/logo_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/finegrain-ai/refiners/main/assets/logo_light.png">
  <img alt="Finegrain Refiners Library" width="352" height="128" style="max-width: 100%;">
</picture>

**The simplest way to train and run adapters on top of foundation models**

[**Manifesto**](https://refine.rs/home/why/) |
[**Docs**](https://refine.rs) |
[**Guides**](https://refine.rs/guides/adapting_sdxl/) |
[**Discussions**](https://github.com/finegrain-ai/refiners/discussions) |
[**Discord**](https://discord.gg/mCmjNUVV7d)

______________________________________________________________________

[![dependencies - Rye](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/rye/main/artwork/badge.json)](https://github.com/astral-sh/rye)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![packaging - Hatch](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/refiners)](https://pypi.org/project/refiners/)
[![PyPI - Status](https://badge.fury.io/py/refiners.svg)](https://pypi.org/project/refiners/)
[![license](https://img.shields.io/badge/license-MIT-blue)](/LICENSE) \
[![code bounties](https://img.shields.io/badge/code-bounties-blue)](https://finegrain.ai/bounties)
[![Discord](https://img.shields.io/discord/1179456777406922913?logo=discord&logoColor=white&color=%235765F2)](https://discord.gg/mCmjNUVV7d)
[![HuggingFace - Refiners](https://img.shields.io/badge/refiners-ffd21e?logo=huggingface&labelColor=555)](https://huggingface.co/refiners)
[![HuggingFace - Finegrain](https://img.shields.io/badge/finegrain-ffd21e?logo=huggingface&labelColor=555)](https://huggingface.co/finegrain)
[![ComfyUI Registry](https://img.shields.io/badge/ComfyUI_Registry-comfyui--refiners-1a56db)](https://registry.comfy.org/publishers/finegrain/nodes/comfyui-refiners)

</div>

## Latest News 🔥

- Added [ELLA](https://arxiv.org/abs/2403.05135) for better prompts handling (contributed by [@ily-R](https://github.com/ily-R))
- Added the Box Segmenter all-in-one solution ([model](https://huggingface.co/finegrain/finegrain-box-segmenter), [HF Space](https://huggingface.co/spaces/finegrain/finegrain-object-cutter))
- Added [MVANet](https://arxiv.org/abs/2404.07445) for high resolution segmentation
- Added [IC-Light](https://github.com/lllyasviel/IC-Light) to manipulate the illumination of images
- Added Multi Upscaler for high-resolution image generation, inspired from [Clarity Upscaler](https://github.com/philz1337x/clarity-upscaler) ([HF Space](https://huggingface.co/spaces/finegrain/enhancer))
- Added [HQ-SAM](https://arxiv.org/abs/2306.01567) for high quality mask prediction with Segment Anything
- ...see past [releases](https://github.com/finegrain-ai/refiners/releases)

## Installation

The current recommended way to install Refiners is from source using [Rye](https://rye-up.com/):

```bash
git clone "git@github.com:finegrain-ai/refiners.git"
cd refiners
rye sync --all-features
```

## Documentation

Refiners comes with a MkDocs-based documentation website available at https://refine.rs. You will find there a [quick start guide](https://refine.rs/getting-started/recommended/), a description of the [key concepts](https://refine.rs/concepts/chain/), as well as in-depth foundation model adaptation [guides](https://refine.rs/guides/adapting_sdxl/).

## Projects using Refiners

- [Finegrain Editor](https://editor.finegrain.ai/signup?utm_source=github&utm_campaign=refiners): use state-of-the-art visual AI skills to edit product photos
- [Visoid](https://www.visoid.com/): AI-powered architectural visualization
- [brycedrennan/imaginAIry](https://github.com/brycedrennan/imaginAIry): Pythonic AI generation of images and videos
- [chloedia/layerdiffuse](https://github.com/chloedia/layerdiffuse): an implementation of [LayerDiffuse](https://arxiv.org/abs/2402.17113v3) (foreground generation only)

## Awesome Adaptation Papers

If you're interested in understanding the diversity of use cases for foundation model adaptation (potentially beyond the specific adapters supported by Refiners), we suggest you take a look at these outstanding papers:

- [ControlNet](https://arxiv.org/abs/2302.05543)
- [T2I-Adapter](https://arxiv.org/abs/2302.08453)
- [IP-Adapter](https://arxiv.org/abs/2308.06721)
- [Medical SAM Adapter](https://arxiv.org/abs/2304.12620)
- [3DSAM-adapter](https://arxiv.org/abs/2306.13465)
- [SAM-adapter](https://arxiv.org/abs/2304.09148)
- [Cross Modality Attention Adapter](https://arxiv.org/abs/2307.01124)
- [UniAdapter](https://arxiv.org/abs/2302.06605)

## Ape Scout（ApeWisdom 选股工具）

本仓库新增了一个名为 **Ape Scout** 的数据采集与报表工具，用于每天从 [ApeWisdom](https://apewisdom.io/) 获取社区热度数据，并结合 [polygon.io](https://polygon.io/) 的行情、市值信息构建多维筛选器和趋势报表，帮助发现潜在的 10 倍股。

### 快速开始

1. 安装依赖：

   ```bash
   uv pip install -r requirements.lock
   ```

2. 配置环境变量：

   ```bash
   export POLYGON_API_KEY="<你的 polygon.io API key>"
   # 可选：export APEWISDOM_FILTER="all-stocks"
   # 可选：export APESCOUT_DATABASE_URL="sqlite:///./ape_scout.db"
   ```

3. 运行采集任务（建议每日定时运行一次）：

   ```bash
   python -m scripts.ape_scout_ingest --verbose
   ```

4. 启动可视化界面：

   ```bash
   python -m scripts.run_ape_scout_app --host 0.0.0.0 --port 8000
   ```

浏览器访问 `http://127.0.0.1:8000` 即可查看最新的排名、Mentions/Upvotes 趋势、市值和行业过滤器。界面支持分页（10-100 条/页）、多行业筛选、Mentions/Upvotes 区间筛选、最近 N 天趋势折线图以及“每日均有提及”过滤条件，方便寻找潜在的 10 倍股。

## Credits

We took inspiration from these great projects:

- [tinygrad](https://github.com/tinygrad/tinygrad) - For something between PyTorch and [karpathy/micrograd](https://github.com/karpathy/micrograd)
- [Composer](https://github.com/mosaicml/composer) - A PyTorch Library for Efficient Neural Network Training
- [Keras](https://github.com/keras-team/keras) - Deep Learning for humans

## Citation

```bibtex
@misc{the-finegrain-team-2023-refiners,
  author = {Benjamin Trom and Pierre Chapuis and Cédric Deltheil},
  title = {Refiners: The simplest way to train and run adapters on top of foundation models},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/finegrain-ai/refiners}}
}
```
