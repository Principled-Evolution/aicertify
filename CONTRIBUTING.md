# 🛠️ Contributing to AICertify 🚀

Thank you for your interest in contributing to **AICertify**! 🎉  
We welcome contributions from developers, AI practitioners, and governance professionals.

## 📌 Ways to Contribute
### **1️⃣ Reporting Issues**
- Found a bug or incorrect validation? [Open a GitHub Issue](https://github.com/mantric/AICertify/issues).
- Before posting, search existing issues to **avoid duplicates**.

### **2️⃣ Feature Requests & Discussions**
- Have an idea for improvement? **Start a discussion!**  
  👉 [Join GitHub Discussions](https://github.com/mantric/AICertify/discussions)  
- If it's a major proposal, we recommend **creating an issue first**.

### **3️⃣ Contributing Code**
We accept **bug fixes, new policies, API improvements, and documentation updates**.  

#### **📜 Setting Up Your Development Environment**
1. **Fork the Repository** & Clone:
   ```bash
   git clone https://github.com/mantric/AICertify.git
   cd AICertify
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Tests Before Pushing**:
   ```bash
   python cli.py --category compliance/eu_ai_act --input examples/input_examples.json
   ```

4. **Create a Feature Branch**:
   ```bash
   git checkout -b feature-new-policy
   ```

5. **Commit & Push Your Changes**:
   ```bash
   git commit -m "Added new AI fairness policy"
   git push origin feature-new-policy
   ```

6. **Create a Pull Request (PR)**:
   - **Title**: Be concise but descriptive.
   - **Description**: Explain why this PR improves AICertify.
   - **Check CI Logs**: Ensure tests pass before requesting a review.

### **4️⃣ Writing OPA Policies**
We encourage contributions to **regulatory compliance**, **functional validation**, and **acceptance criteria**.  

#### **📝 Example Contribution: New OPA Policy**
📄 **`policies/compliance/new_policy.rego`**
```rego
package compliance.custom_policy

default allow = false

allow {
    input.some_metric < 0.1
}
```

Add an **example input file** in `examples/`, update `README.md`, and test it.

---

## 📜 **Code of Conduct**
By contributing, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md) (to be added soon).

## ✅ **Contribution Checklist**
☑ Code follows project conventions.  
☑ New policies include test cases in `examples/`.  
☑ No breaking changes without discussion.  
☑ All contributions follow [semantic commit messages](https://www.conventionalcommits.org/).  

## 🏷️ Issue & PR Labels
We use **GitHub Labels** to track work:
- 🐞 `bug` → Report issues.
- 🚀 `enhancement` → New features.
- 🎯 `validation` → AI correctness checks.
- 📜 `compliance` → AI governance & policies.
- 📝 `documentation` → Docs, examples, & guides.

👉 [See all labels here](https://github.com/mantric/AICertify/labels).

🚀 **Thank you for making AI governance better with AICertify!** 🎉
