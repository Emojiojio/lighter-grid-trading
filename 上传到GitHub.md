# 上传代码到 GitHub - 详细步骤

## 📋 当前状态
✅ 代码已准备好并提交到本地 Git 仓库  
❌ GitHub 上还没有创建 `lighter-grid-trading` 仓库

## 🚀 上传步骤

### 步骤 1：在 GitHub 上创建仓库

1. **打开浏览器，访问：**
   ```
   https://github.com/new
   ```

2. **确保已登录账号** `emojiojio`

3. **填写仓库信息：**
   - **Repository name**: `lighter-grid-trading`
   - **Description**: `Lighter 交易所网格交易策略`
   - **Visibility**: 选择 Public（公开）或 Private（私有）
   - ⚠️ **重要**：不要勾选以下选项：
     - ❌ "Add a README file"
     - ❌ "Add .gitignore"
     - ❌ "Choose a license"
   - 保持所有选项为空

4. **点击绿色的 "Create repository" 按钮**

### 步骤 2：获取 Personal Access Token

由于 GitHub 不再支持密码登录，需要使用 Token：

1. **访问 Token 设置页面：**
   ```
   https://github.com/settings/tokens
   ```

2. **点击 "Generate new token" → "Generate new token (classic)"**

3. **填写 Token 信息：**
   - **Note**: `lighter-grid-trading`（备注名称）
   - **Expiration**: 选择过期时间（建议 90 天或 No expiration）
   - **Select scopes**: 勾选 `repo`（完整仓库权限）

4. **点击 "Generate token"**

5. **复制 Token**（只显示一次，请立即保存）
   - Token 格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 步骤 3：推送代码到 GitHub

在终端执行以下命令：

```bash
cd /Users/flock-studio/Documents/lighter-grid-trading
git push -u origin main
```

**当提示输入时：**
- **Username**: `emojiojio`
- **Password**: 粘贴您刚才复制的 Personal Access Token（不是 GitHub 密码）

### 步骤 4：验证上传成功

推送成功后，访问：
```
https://github.com/emojiojio/lighter-grid-trading
```

您应该能看到所有代码文件。

---

## 🔄 如果遇到问题

### 问题 1：提示 "repository not found"
**解决**：确保已在 GitHub 上创建了仓库，仓库名完全匹配 `lighter-grid-trading`

### 问题 2：提示 "Authentication failed"
**解决**：
- 确认 Token 是否正确复制（没有多余空格）
- 确认 Token 有 `repo` 权限
- 尝试重新生成 Token

### 问题 3：提示 "could not read Username"
**解决**：
- 使用 Personal Access Token 而不是密码
- 如果使用 macOS Keychain，可能需要清除旧的凭据：
  ```bash
  git credential-osxkeychain erase
  host=github.com
  protocol=https
  ```
  然后重新推送

### 问题 4：想使用 SSH 方式
**解决**：
1. 配置 SSH 密钥（如果还没有）：
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   cat ~/.ssh/id_ed25519.pub
   ```
   复制公钥，在 GitHub Settings → SSH and GPG keys 中添加

2. 更改远程 URL：
   ```bash
   git remote set-url origin git@github.com:emojiojio/lighter-grid-trading.git
   git push -u origin main
   ```

---

## ✅ 完成后的检查清单

- [ ] GitHub 仓库已创建
- [ ] Personal Access Token 已生成
- [ ] 代码已成功推送
- [ ] 可以在 GitHub 上看到所有文件
- [ ] README.md 正常显示

---

## 📝 后续更新代码

以后修改代码后，使用以下命令更新：

```bash
# 添加修改的文件
git add .

# 提交更改
git commit -m "描述您的更改"

# 推送到 GitHub
git push
```

---

祝您上传顺利！🎉

