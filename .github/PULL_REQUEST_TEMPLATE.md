---
name: "🚀 Pull Request"
about: Submit a new feature, bug fix, or improvement
title: "[PR] Short Description"
labels: enhancement
assignees: ""

---

## 🚀 Overview
A clear and concise description of what this PR does.

## 🔍 Related Issues
Closes #123 (if applicable)

## 📜 Changes Made
- ✅ [List major changes]
- ✅ [Mention updated policies, API endpoints, CLI tools]
- ✅ [Describe how the changes impact AI validation]

## 🎯 How to Test
1. Run `python cli.py --category compliance/eu_ai_act --input examples/input_examples.json`
2. Start the API: `uvicorn service:app --reload`
3. Send a request:
   ```bash  
   curl -X POST "http://localhost:8000/validate" -H "Content-Type: application/json" -d '{"category": "compliance/eu_ai_act", "input_data": {"bias_score": 0.03}}'
   ```

## 📷 Screenshots (if applicable)
If applicable, add screenshots to help explain the changes.

## 📄 Detailed Description
Provide a detailed description of the changes made.

## 📚 Documentation
- ✅ [Updated README.md]
- ✅ [Added new examples]
- ✅ [Updated API documentation]

