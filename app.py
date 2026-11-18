
import ast
import os
import re
import subprocess
import sys
import tempfile
import streamlit as st

# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="GenAI Code Platform",
    page_icon="💻",
    layout="wide"
)

st.title(
    "💻 Generative AI-Based Code Generation, "
    "Debugging & Optimization Platform"
)

st.caption(
    "Academic Prototype | Code Generation | Debugging | "
    "Optimization | Testing & Validation"
)


# --------------------------------------------------
# GEMINI AI CONNECTION
# --------------------------------------------------

def get_api_key():
    try:
        return st.secrets.get(
            "GEMINI_API_KEY",
            os.getenv("GEMINI_API_KEY", "")
        )
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")



def ask_gemi
def ask_gemini(prompt):

    api_key = get_api_key()

    if not api_key:
        return None, "Demo Mode"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level="low"
                ),
                max_output_tokens=2048
            )
        )

        return response.text.strip(), "Gemini AI"

    except Exception as error:
        return None, f"Gemini Error: {error}"



# --------------------------------------------------
# COMMON FUNCTIONS
# --------------------------------------------------

def extract_code(text):

    if not text:
        return ""

    match = re.search(
        r"```(?:python|py)?\s*(.*?)```",
        text,
        flags=re.I | re.S
    )

    if match:
        return match.group(1).strip()

    return text.strip()


def syntax_check(source):

    try:
        ast.parse(source)
        return True, "Syntax validation passed."

    except SyntaxError as error:
        return False, (
            f"SyntaxError on line {error.lineno}: "
            f"{error.msg}"
        )


def run_python_demo(source, timeout=4):

    # Academic prototype only.
    # This is NOT a secure sandbox.

    with tempfile.TemporaryDirectory() as folder:

        file_path = os.path.join(
            folder,
            "candidate.py"
        )

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(source)

        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=folder
            )

            return (
                result.returncode,
                result.stdout,
                result.stderr
            )

        except subprocess.TimeoutExpired:
            return -1, "", "Execution timed out."


def display_ai_result(
    prompt,
    fallback_code,
    fallback_explanation
):

    answer, source = ask_gemini(prompt)

    if answer:
        return (
            extract_code(answer),
            answer,
            source
        )

    return (
        fallback_code,
        fallback_explanation,
        source
    )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("Platform Settings")

    if get_api_key():
        st.success("Gemini API Connected")
    else:
        st.info("Demo Mode - No API Key")

    st.caption(
        "Add GEMINI_API_KEY under Streamlit "
        "Settings → Secrets to enable live AI."
    )


# --------------------------------------------------
# FOUR MODULE TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Code Generation",
    "2️⃣ Debugging",
    "3️⃣ Optimization",
    "4️⃣ Testing & Validation"
])


# ==================================================
# MODULE 1: CODE GENERATION
# ==================================================

with tab1:

    st.header(
        "Module 1 – Prompt Processing & Code Generation"
    )

    requirement = st.text_area(
        "Describe the program you want",

        "Write a Python function that checks "
        "whether a number is odd or even.",

        height=110,
        key="module1_prompt"
    )

    constraints = st.text_input(
        "Optional Constraints",

        "Use a function and include a sample call.",

        key="module1_constraints"
    )

    if st.button(
        "✨ Generate Code",
        key="module1_generate",
        type="primary"
    ):

        prompt = f"""
You are an expert programming assistant.

Generate a correct and complete beginner-friendly
Python program for this request:

{requirement}

Constraints:
{constraints}

Return:
1. Complete Python code inside a Python code block.
2. A concise explanation.
3. Example output if relevant.

Do not claim that code has been executed unless
it has actually been executed.
"""

        fallback = '''def is_odd(number):
    return number % 2 != 0

number = 7

if is_odd(number):
    print(number, "is odd")
else:
    print(number, "is even")
'''

        code, explanation, source = display_ai_result(
            prompt,
            fallback,
            "Demonstration fallback: checks whether 7 is odd. "
            "Connect Gemini for dynamic responses."
        )

        st.session_state["generated_code"] = code

        st.session_state["generated_explanation"] = (
            explanation
        )

        st.session_state["generated_source"] = source

    if "generated_code" in st.session_state:

        st.caption(
            "Response Source: "
            + st.session_state.get(
                "generated_source",
                "Demo"
            )
        )

        st.subheader("Generated Code")

        st.code(
            st.session_state["generated_code"],
            language="python"
        )

        ok, message = syntax_check(
            st.session_state["generated_code"]
        )

        if ok:
            st.success(message)
        else:
            st.error(message)

        with st.expander("Code Explanation"):

            st.write(
                st.session_state.get(
                    "generated_explanation",
                    ""
                )
            )


# ==================================================
# MODULE 2: AUTOMATED DEBUGGING
# ==================================================

with tab2:

    st.header(
        "Module 2 – Automated Debugging & Error Explanation"
    )

    debug_default = st.session_state.get(
        "generated_code",

        '''def divide(a, b):
    return a / b

print(divide(10, 0))
'''
    )

    buggy_code = st.text_area(
        "Paste the Python code you want to debug",

        debug_default,

        height=200,

        key="module2_input"
    )

    if st.button(
        "🐞 Detect and Repair Error",
        key="module2_debug",
        type="primary"
    ):

        syntax_ok, syntax_message = syntax_check(
            buggy_code
        )

        if not syntax_ok:

            diagnostic = syntax_message

        else:

            return_code, stdout, stderr = (
                run_python_demo(buggy_code)
            )

            if return_code != 0:
                diagnostic = stderr

            else:
                diagnostic = (
                    "Program executed without a runtime error.\n"
                    "Output:\n" + (stdout or "(No output)")
                )

        st.session_state["debug_diagnostic"] = diagnostic

        prompt = f"""
You are an expert Python debugging assistant.

Analyze the code and diagnostic.

Explain the root cause and provide a corrected
version with the smallest reasonable change.

Preserve intended behavior and function names.

Return corrected code in a Python code block,
followed by an explanation.

CODE:
{buggy_code}

DIAGNOSTIC:
{diagnostic}
"""

        fallback = '''def divide(a, b):
    if b == 0:
        raise ValueError(
            "The denominator must not be zero"
        )

    return a / b

print(divide(10, 2))
'''

        repaired, explanation, source = display_ai_result(
            prompt,
            fallback,
            "Demonstration repair for division by zero. "
            "Connect Gemini for tailored repairs."
        )

        st.session_state["repaired_code"] = repaired

        st.session_state["repair_explanation"] = (
            explanation
        )

        st.session_state["repair_source"] = source

    if "debug_diagnostic" in st.session_state:

        st.subheader("Detected Diagnostic")

        st.code(
            st.session_state["debug_diagnostic"]
        )

        st.subheader("Suggested Corrected Code")

        st.code(
            st.session_state.get(
                "repaired_code",
                ""
            ),
            language="python"
        )

        st.caption(
            "Response Source: "
            + st.session_state.get(
                "repair_source",
                "Demo"
            )
        )

        with st.expander("Root Cause Explanation"):

            st.write(
                st.session_state.get(
                    "repair_explanation",
                    ""
                )
            )


# ==================================================
# MODULE 3: CODE OPTIMIZATION
# ==================================================

with tab3:

    st.header(
        "Module 3 – Code Optimization & Quality Analysis"
    )

    original_code = st.text_area(
        "Paste the Python code you want to optimize",

        '''def find_duplicates(items):
    duplicates = []

    for item in items:

        if items.count(item) > 1 and item not in duplicates:
            duplicates.append(item)

    return duplicates
''',

        height=200,

        key="module3_input"
    )

    if st.button(
        "⚡ Analyze and Optimize",
        key="module3_optimize",
        type="primary"
    ):

        findings = []

        try:

            tree = ast.parse(original_code)

            for node in ast.walk(tree):

                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "count"
                ):

                    findings.append(
                        "Repeated .count() call detected; "
                        "it may repeatedly scan a list."
                    )

            if not findings:

                findings.append(
                    "No .count() pattern detected by "
                    "this simple static inspection."
                )

        except SyntaxError as error:

            findings.append(
                f"Syntax error: {error}"
            )

        prompt = f"""
You are an expert Python performance
and code-quality assistant.

Review this code for:

1. Duplicate operations
2. Unnecessary computation
3. Readability
4. Algorithmic complexity
5. Memory usage

Suggest an equivalent optimized version
where possible.

Explain time and space complexity.

Do not claim measured speed improvements.

Return optimized code in a Python code block,
followed by an explanation.

CODE:
{original_code}
"""

        fallback = '''def find_duplicates(items):

    seen = set()
    duplicates = set()

    for item in items:

        if item in seen:
            duplicates.add(item)

        else:
            seen.add(item)

    return list(duplicates)
'''

        optimized, explanation, source = display_ai_result(
            prompt,
            fallback,
            "Demonstration optimization using sets "
            "instead of repeated list.count() calls."
        )

        st.session_state["optimization_findings"] = (
            findings
        )

        st.session_state["optimized_code"] = optimized

        st.session_state["optimization_explanation"] = (
            explanation
        )

        st.session_state["optimization_source"] = source

    if "optimized_code" in st.session_state:

        st.subheader("Static Inspection Findings")

        for finding in st.session_state.get(
            "optimization_findings",
            []
        ):

            st.write("• " + finding)

        st.subheader("Optimized Code")

        st.code(
            st.session_state["optimized_code"],
            language="python"
        )

        st.caption(
            "Response Source: "
            + st.session_state.get(
                "optimization_source",
                "Demo"
            )
        )

        with st.expander("Optimization Explanation"):

            st.write(
                st.session_state.get(
                    "optimization_explanation",
                    ""
                )
            )

        st.info(
            "Verify functional equivalence and measure "
            "both versions with identical inputs before "
            "claiming performance gains."
        )


# ==================================================
# MODULE 4: TESTING AND VALIDATION
# ==================================================

with tab4:

    st.header(
        "Module 4 – Testing, Validation & User Workspace"
    )

    validation_default = st.session_state.get(
        "generated_code",

        '''def add(a, b):
    return a + b

print(add(2, 3))
'''
    )

    validation_code = st.text_area(
        "Python code to validate and execute",

        validation_default,

        height=200,

        key="module4_input"
    )

    if st.button(
        "🧪 Run Validation",
        key="module4_validate",
        type="primary"
    ):

        syntax_ok, syntax_message = syntax_check(
            validation_code
        )

        st.subheader("Syntax Validation")

        if syntax_ok:

            st.success(syntax_message)

            return_code, stdout, stderr = (
                run_python_demo(validation_code)
            )

            st.subheader("Execution Result")

            if return_code == 0:

                st.success("Execution Passed.")

            else:

                st.error("Execution Failed.")

            st.text_area(
                "Standard Output",
                stdout or "(No output)",
                height=90
            )

            st.text_area(
                "Error Output",
                stderr or "(No errors)",
                height=90
            )

            st.metric(
                "Validation Status",
                "PASSED" if return_code == 0 else "FAILED"
            )

        else:

            st.error(syntax_message)

            st.metric(
                "Validation Status",
                "FAILED"
            )

    st.warning(
        "Academic prototype only: code execution is not "
        "isolated in a hardened sandbox. Do not execute "
        "untrusted code."
    )


# ==================================================
# END-TO-END WORKFLOW
# ==================================================

st.divider()

st.subheader("End-to-End System Workflow")

st.markdown(
    """
    **User Requirement**
    
    ↓
    
    **Prompt Processing**
    
    ↓
    
    **AI Code Generation**
    
    ↓
    
    **Syntax and Runtime Validation**
    
    ↓
    
    **Diagnostic Feedback**
    
    ↓
    
    **AI-Guided Repair**
    
    ↓
    
    **Code Optimization**
    
    ↓
    
    **Testing and Validation**
    
    ↓
    
    **Validated Output**
    """
)

st.caption(
    "Without a Gemini API key, the app uses demonstration "
    "fallbacks. With a valid key, generation, debugging "
    "and optimization use Gemini responses."
)
