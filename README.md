# 发电企业对标数据来源公开网站

这个目录是可公开发布的静态网站版本，只包含网页和说明文件，不包含 Word 原稿、临时解析文件、下载的PDF或内部数据文件。

## 文件说明

- `index.html`：公开网站首页，打开后直接进入数据来源导航页面。
- `data_sources.html`：同一页面的备用文件名，方便保留原始访问路径。
- `.nojekyll`：用于 GitHub Pages，避免静态资源被 Jekyll 处理。

## 发布方式

### GitHub Pages

1. 新建一个 GitHub 仓库。
2. 只上传 `public_site` 目录里的文件。
3. 在仓库 `Settings` -> `Pages` 中启用 Pages。
4. Source 选择 `Deploy from a branch`，Branch 选择 `main`，目录选择 `/root`。
5. 保存后，GitHub 会生成一个公开网址。

### Cloudflare Pages / Netlify / Vercel

1. 新建静态站项目。
2. 上传或连接这个 `public_site` 目录。
3. Build command 留空。
4. Output directory 留空或选择根目录。
5. 发布后入口为 `index.html`。

## 公开前检查

- 不上传 `中国发电企业和世界同类能源企业对标分析报告...docx`。
- 不上传 `.codex_extract`。
- 不上传临时下载的 PDF、JSON 或其他解析中间文件。
- 只公开已经在网页中注明来源、口径和官方链接的数据。
- 2025数据中凡未确认集团/母公司合并口径的，继续保留“未发布”“未取得”或“不能填数”。
