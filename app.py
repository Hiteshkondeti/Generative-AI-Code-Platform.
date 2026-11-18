import ast, os, re, subprocess, sys, tempfile
import streamlit as st

st.set_page_config(page_title="GenAI Code Platform", page_icon="💻", layout="wide")
st.title("💻 Generative AI-Based Code Generation, Debugging & Optimization Platform")
st.caption("Academic prototype | Code generation • Debugging • Optimization • Testing & validation")

def ask_ai(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    if not api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text or ""
    except Exception as exc:
        st.warning(f"AI API unavailable; using demo mode. Details: {exc}")
        return None

def extract_code(text):
    match = re.search(r"```(?:python)?\s*(.*?)```", text, flags=re.I | re.S)
    return match.group(1).strip() if match else text.strip()

def syntax_check(source):
    try:
        ast.parse(source)
        return True, "Syntax validation passed."
    except SyntaxError as exc:
        return False, f"SyntaxError on line {exc.lineno}: {exc.msg}"

def run_code_demo(source, timeout=3):
    # Academic demonstration only; this is NOT a secure sandbox.
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "candidate.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)
        try:
            result = subprocess.run([sys.executable, path], capture_output=True,
                                    text=True, timeout=timeout, cwd=folder)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Execution timed out."

tabs = st.tabs(["1️⃣ Code Generation", "2️⃣ Debugging", "3️⃣ Optimization", "4️⃣ Testing & Validation"])

with tabs[0]:
    st.header("Module 1 – Prompt Processing & Code Generation")
    requirement = st.text_area("Describe the program you want",
        "Write a Python function that checks whether a number is prime.", height=100)
    if st.button("✨ Generate Code"):
        prompt = f'''Generate complete Python code for this requirement:
{requirement}
Return code in a Python fenced block and a brief explanation.'''
        answer = ask_ai(prompt)
        if answer:
            generated = extract_code(answer)
            st.session_state.generation_mode = "Live Gemini AI"
            st.session_state.generation_explanation = answer
        else:
            generated = '''def is_prime(number):
    if number < 2:
        return False
    for divisor in range(2, int(number ** 0.5) + 1):
        if number % divisor == 0:
            return False
    return True

print(is_prime(17))
'''
            st.session_state.generation_mode = "Built-in demonstration (no API key)"
            st.session_state.generation_explanation = "Checks divisors up to the square root of the number."
        st.session_state.generated_code = generated
    if "generated_code" in st.session_state:
        st.caption("Mode: " + st.session_state.get("generation_mode", "Demo"))
        st.code(st.session_state.generated_code, language="python")
        ok, msg = syntax_check(st.session_state.generated_code)
        st.success(msg) if ok else st.error(msg)
        st.write(st.session_state.get("generation_explanation", ""))

with tabs[1]:
    st.header("Module 2 – Automated Debugging & Error Explanation")
    default_bug = '''def divide(a, b):
    return a / b

print(divide(10, 0))
'''
    buggy = st.text_area("Paste Python code containing an error", default_bug, height=170)
    if st.button("🐞 Detect and Repair Error"):
        ok, msg = syntax_check(buggy)
        if not ok:
            diagnostic = msg
        else:
            rc, stdout, stderr = run_code_demo(buggy)
            diagnostic = stderr if rc != 0 else "Program ran successfully.\\n" + stdout
        st.subheader("Diagnostic")
        st.code(diagnostic)
        if "ZeroDivisionError" in diagnostic:
            st.warning("Root cause: division by zero. Check the denominator before division.")
            fallback = '''def divide(a, b):
    if b == 0:
        raise ValueError("The denominator must not be zero")
    return a / b

print(divide(10, 2))
'''
        else:
            fallback = buggy
        prompt = f'''Repair this Python program with a minimal change.
Return corrected code in a Python fenced block.
SOURCE:
{buggy}
DIAGNOSTIC:
{diagnostic}'''
        answer = ask_ai(prompt)
        repaired = extract_code(answer) if answer else fallback
        st.subheader("Suggested corrected code")
        st.code(repaired, language="python")
        st.caption("Live Gemini AI repair" if answer else "Built-in demonstration repair")

with tabs[2]:
    st.header("Module 3 – Code Optimization & Quality Analysis")
    original = st.text_area("Original Python code", '''def find_duplicates(items):
    duplicates = []
    for item in items:
        if items.count(item) > 1 and item not in duplicates:
            duplicates.append(item)
    return duplicates
''', height=170)
    if st.button("⚡ Analyze and Optimize"):
        findings = []
        try:
            tree = ast.parse(original)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "count":
                    findings.append("Repeated .count() call may cause unnecessary list scanning.")
            if not findings:
                findings.append("No simple .count() performance warning detected.")
        except SyntaxError as exc:
            findings.append(f"Syntax error: {exc}")
        st.subheader("Static inspection")
        for item in findings:
            st.write("•", item)
        prompt = f'''Optimize this Python code without changing behavior.
Explain the changes and complexity. Return code in a Python fenced block.
{original}'''
        answer = ask_ai(prompt)
        if answer:
            optimized = extract_code(answer)
            st.caption("Live Gemini AI suggestion")
        else:
            optimized = '''def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
'''
            st.caption("Built-in demonstration optimization")
        st.subheader("Optimized candidate")
        st.code(optimized, language="python")
        st.info("Test both versions with identical inputs. Shorter code is not automatically faster.")

with tabs[3]:
    st.header("Module 4 – Testing, Validation & User Workspace")
    default_test = st.session_state.get("generated_code", '''def add(a, b):
    return a + b

print(add(2, 3))
''')
    source = st.text_area("Python code to validate", default_test, height=170)
    if st.button("🧪 Run Validation"):
        ok, msg = syntax_check(source)
        st.write("Syntax check:", "✅ Passed" if ok else "❌ Failed")
        st.code(msg)
        if ok:
            rc, stdout, stderr = run_code_demo(source)
            st.write("Execution status:", "✅ Passed" if rc == 0 else "❌ Failed")
            st.text_area("Standard output", stdout or "(No output)", height=80)
            st.text_area("Error output", stderr or "(No errors)", height=80)
            st.metric("Validation status", "PASSED" if rc == 0 else "FAILED")
        st.warning("Prototype only: execution is not isolated in a hardened sandbox. Do not run untrusted code.")

st.divider()
st.subheader("End-to-end workflow")
st.markdown("**Requirement → Prompt processing → Code generation → Syntax/runtime checks → Debugging → Optimization → Testing → Validated output**")
st.caption("Without a Gemini key, all modules remain usable with built-in demonstration examples.")
