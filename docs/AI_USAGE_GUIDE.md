# Quick Reference: Using AI Prompts for This Project

## 📁 Files Created for You

1. **`/docs/REFACTOR_TO_PLUGIN_ARCHITECTURE.md`**  
   - High-level architecture plan
   - For humans to understand the design
   - Reference during interviews

2. **`/docs/prompts/IMPLEMENT_PLUGIN_ARCHITECTURE.md`**  
   - Step-by-step implementation guide
   - For AI agents (Claude, Copilot, etc.)
   - Copy/paste to AI to implement

3. **`/.cursorrules`**  
   - Project-specific AI behavior rules
   - Cursor reads this automatically
   - Ensures consistency across AI sessions

---

## 🤖 How to Use with Different AI Tools

### Option 1: Cursor IDE (Recommended)

**Cursor automatically reads `.cursorrules` file!**

1. Open project in Cursor: `cursor /Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub`

2. Start new chat (Cmd+L or Ctrl+L)

3. Say:
```
Please implement the plugin architecture refactor described in:
docs/prompts/IMPLEMENT_PLUGIN_ARCHITECTURE.md

Start with Phase 1 (Base Infrastructure). 
Read the file and show me your implementation plan before coding.
```

4. Cursor will:
   - Read the `.cursorrules` file automatically
   - Follow the project conventions
   - Implement step by step
   - Ask for approval at each phase

**Advantages:**
- ✅ Reads project rules automatically
- ✅ Can see your entire codebase
- ✅ Best for large refactors

---

### Option 2: VSCode with GitHub Copilot Chat

1. Open project in VSCode

2. Open Copilot Chat panel

3. Use `@workspace` to give it project context:
```
@workspace I need to implement a plugin architecture for data sources.

Please read and follow the plan in:
docs/prompts/IMPLEMENT_PLUGIN_ARCHITECTURE.md

Also review the project rules in .cursorrules

Start with Phase 1. Show me your plan first.
```

4. For each file it creates, review and approve

**Advantages:**
- ✅ Works in standard VSCode
- ✅ Good for smaller tasks
- ⚠️ Doesn't auto-read .cursorrules (must reference manually)

---

### Option 3: Claude.ai Web Interface (This Conversation)

1. Upload the prompt file:
   - Go to claude.ai
   - Click attachment button
   - Upload: `docs/prompts/IMPLEMENT_PLUGIN_ARCHITECTURE.md`

2. Say:
```
I need you to guide me through implementing the plugin architecture 
described in the uploaded document.

Walk me through Phase 1 step by step.
For each file, show me the complete code.
I'll create the files manually.
```

3. Claude will guide you through each phase

4. You manually create files based on Claude's code

**Advantages:**
- ✅ Most detailed explanations
- ✅ Best for learning while implementing
- ⚠️ You have to create files manually

---

### Option 4: Claude via API (Advanced)

If you have API access, you can:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

# Read the prompt file
with open("docs/prompts/IMPLEMENT_PLUGIN_ARCHITECTURE.md") as f:
    prompt = f.read()

# Ask Claude to implement Phase 1
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    messages=[{
        "role": "user",
        "content": f"{prompt}\n\nImplement Phase 1 (Base Infrastructure)"
    }]
)

print(response.content[0].text)
```

---

## 📝 Recommended Workflow

### For This Refactor Specifically:

**STEP 1: Use Cursor for Implementation (Best)**

```bash
# Open in Cursor
cursor /Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub

# In Cursor chat:
"Implement Phase 1 of docs/prompts/IMPLEMENT_PLUGIN_ARCHITECTURE.md

Before coding, show me:
1. Which files you'll create
2. The order you'll create them
3. Any questions about the requirements"
```

**STEP 2: After Each Phase, Test**

```bash
# Run the pipeline
python src/ingestion/pipeline.py

# Should still output: 113 documents, 100% quality
```

**STEP 3: Use Claude.ai for Understanding**

If you want to understand WHY something works:

```
Upload the file Cursor just created and ask:

"Explain how this DataSource abstract base class works.
Why do we need all 5 methods?
What design patterns are being used?"
```

**STEP 4: Version Control**

```bash
# After each successful phase:
git add .
git commit -m "feat: Complete Phase X of plugin architecture"
```

---

## 🎯 When to Use Which Prompt File

### Use `REFACTOR_TO_PLUGIN_ARCHITECTURE.md` when:
- ✅ Explaining the architecture to someone
- ✅ Preparing for interview (reference)
- ✅ Understanding the big picture
- ✅ Deciding if refactor is worth it

### Use `IMPLEMENT_PLUGIN_ARCHITECTURE.md` when:
- ✅ Actually implementing the refactor
- ✅ Giving to AI agent to code
- ✅ Need step-by-step instructions
- ✅ Want code examples and tests

### Use `.cursorrules` when:
- ✅ Using Cursor IDE (automatic)
- ✅ Want AI to follow project conventions
- ✅ Ensuring consistency across sessions
- ✅ Multiple people working on project

---

## 💡 Pro Tips

### Tip 1: Incremental Implementation

Don't give AI all 7 phases at once. Instead:

```
Session 1: "Implement Phase 1"
[verify it works]

Session 2: "Implement Phase 2 (CSV only)"
[verify it works]

Session 3: "Implement Phase 2 (JSON and XML)"
[verify it works]

...and so on
```

### Tip 2: Ask for Explanation First

Before running code AI generates:

```
"Before I run this, explain:
1. What files did you create?
2. What do they do?
3. How do I test they work?
4. What could go wrong?"
```

### Tip 3: Keep Context Window Clean

AI gets confused with too much context. Start fresh chat when:
- Switching between phases
- Error is resolved
- Starting new feature

### Tip 4: Save Good Prompts

If you find a prompt that works really well:

```bash
# Save it
echo "Your great prompt here" >> docs/prompts/HELPFUL_PROMPTS.md
```

---

## 🆘 Troubleshooting

### Issue: "AI is not following the plan"

**Solution:**
```
"Stop. Re-read docs/prompts/IMPLEMENT_PLUGIN_ARCHITECTURE.md

You're implementing Phase X but should be on Phase Y.
Let's restart from Phase Y, step 1."
```

### Issue: "AI created files in wrong location"

**Solution:**
```
"These files are in the wrong location.

According to .cursorrules, they should be in:
src/ingestion/data_sources/

Please move them there."
```

### Issue: "AI is making up its own approach"

**Solution:**
```
"You're not following the implementation guide.

Please strictly follow:
docs/prompts/IMPLEMENT_PLUGIN_ARCHITECTURE.md

Do not deviate from the plan without asking first."
```

### Issue: "Code doesn't work after AI generated it"

**Solution:**
```
"The code you generated has this error:
[paste exact error]

According to the implementation guide, this step should:
[paste relevant section from guide]

Can you fix the code to match the guide?"
```

---

## 📊 Success Metrics

After using the prompts, you should have:

- [ ] All files created in correct locations
- [ ] Pipeline still runs (113 docs, 100% quality)
- [ ] Zero if/elif chains in pipeline.py
- [ ] Can add PDF in <1 hour
- [ ] All tests passing

---

## 🎓 Learning Path

### If You're New to AI-Assisted Coding:

**Week 1:** Use Claude.ai web interface
- Upload prompt file
- Ask it to explain each phase
- Manually create files based on its code
- Learn by doing

**Week 2:** Use VSCode + Copilot
- Let it suggest code
- You review and approve
- Faster but still hands-on

**Week 3:** Use Cursor
- Let it implement entire phases
- You test and verify
- Fastest but less learning

### If You're Experienced:

**Day 1:** Cursor implements it all
- Give it the full prompt file
- Review each phase
- Test incrementally

---

## 📞 Getting Help

If you get stuck:

1. **Check the docs:**
   - `IMPLEMENT_PLUGIN_ARCHITECTURE.md` - implementation details
   - `.cursorrules` - project conventions
   - `REFACTOR_TO_PLUGIN_ARCHITECTURE.md` - architecture overview

2. **Ask AI for help:**
   ```
   "I'm stuck on Phase X, Task Y.
   
   The error is: [paste error]
   
   According to the guide, I should [paste relevant section].
   
   What am I doing wrong?"
   ```

3. **Start over if needed:**
   ```bash
   # Restore backup
   git checkout HEAD -- src/ingestion/pipeline.py
   
   # Try again with clearer prompts
   ```

---

**Remember:** The AI is a tool. You're the architect. Review everything it creates! 🏗️
