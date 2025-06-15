"""
UI Tab Components for Coding Assistant
Modular UI components to separate presentation logic from business logic
"""
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
import json

from src.config.coding_config import (
    SUPPORTED_LANGUAGES, CODING_TEMPLATES, DATA_SCIENCE_EXAMPLES, 
    REVIEW_ASPECTS, SessionData, get_language_info
)
from src.core.chain_of_thought import ReasoningType
from src.utils.logging import get_logger

logger = get_logger(__name__)


def render_code_generation_tab(coding_assistant, selected_language: str, session_state) -> None:
    """Render the code generation tab UI"""
    st.markdown("### 🚀 Code Generation")
    st.markdown("Generate high-quality code with AI assistance")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Code generation form
        template_type = st.selectbox(
            "**Code Template**",
            options=list(CODING_TEMPLATES.keys()),
            help="Choose a code template to get started"
        )
        
        description = st.text_area(
            "**Code Description**",
            height=100,
            placeholder=f"Describe what you want to create... \n\nExample: {CODING_TEMPLATES[template_type]}\n\nData Science Tip: For data tasks, mention your data format, size, and analysis goals!",
            help="Provide a detailed description of the code you want to generate"
        )
        
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            include_tests = st.checkbox("📝 Include Unit Tests", value=True)
            include_docs = st.checkbox("📖 Include Documentation", value=True)
        
        with col1_2:
            include_comments = st.checkbox("💬 Add Comments", value=True)
            follow_conventions = st.checkbox("⚡ Follow Best Practices", value=True)
        
        if st.button("🚀 Generate Code", type="primary"):
            if description.strip():
                _handle_code_generation(
                    session_state, selected_language, template_type, description,
                    include_tests, include_docs, include_comments, follow_conventions
                )
            else:
                st.warning("⚠️ Please provide a code description")
    
    with col2:
        _render_generation_tips()


def render_code_review_tab(coding_assistant, selected_language: str, session_state) -> None:
    """Render the code review tab UI"""
    st.markdown("### 🔍 Code Review")
    st.markdown("Get comprehensive code analysis and improvement suggestions")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Code review form
        code_input = st.text_area(
            "**Code to Review**",
            height=300,
            placeholder=f"Paste your {selected_language} code here for review...",
            help="Paste the code you want to analyze and improve"
        )
        
        review_aspects = st.multiselect(
            "**Review Focus**",
            options=REVIEW_ASPECTS,
            default=["Code Quality", "Best Practices", "Security"],
            help="Select specific aspects to focus on during review"
        )
        
        if st.button("🔍 Review Code", type="primary"):
            if code_input.strip():
                _handle_code_review(session_state, selected_language, code_input, review_aspects)
            else:
                st.warning("⚠️ Please provide code to review")
    
    with col2:
        _render_review_guidelines()


def render_debug_tab(coding_assistant, selected_language: str, session_state) -> None:
    """Render the debug code tab UI"""
    st.markdown("### 🐛 Debug Code")
    st.markdown("Debug issues and get solutions for code problems")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Debug form
        buggy_code = st.text_area(
            "**Code with Issues**",
            height=200,
            placeholder=f"Paste your problematic {selected_language} code here...",
            help="Provide the code that has issues"
        )
        
        error_message = st.text_area(
            "**Error Message**",
            height=100,
            placeholder="Paste the error message or describe the problem...",
            help="Include any error messages or describe the unexpected behavior"
        )
        
        expected_behavior = st.text_input(
            "**Expected Behavior**",
            placeholder="What should the code do?",
            help="Describe what the code should accomplish"
        )
        
        if st.button("🐛 Debug Code", type="primary"):
            if buggy_code.strip():
                _handle_debug_code(session_state, selected_language, buggy_code, error_message, expected_behavior)
            else:
                st.warning("⚠️ Please provide code to debug")
    
    with col2:
        _render_debug_tips()


def render_learning_tab(coding_assistant, selected_language: str, session_state) -> None:
    """Render the learn & explain tab UI"""
    st.markdown("### 📚 Learn & Explain")
    st.markdown("Get explanations and learn programming concepts")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Learning options
        learning_type = st.radio(
            "**What would you like to learn?**",
            ["Explain Code", "Learn Concept", "Compare Solutions", "Best Practices"],
            help="Choose the type of learning assistance you need"
        )
        
        query_input = _get_learning_input(learning_type, selected_language)
        
        if st.button("📚 Get Explanation", type="primary"):
            if query_input and query_input.strip():
                _handle_learning_request(session_state, selected_language, learning_type, query_input)
            else:
                st.warning("⚠️ Please provide input for explanation")
    
    with col2:
        _render_learning_resources(selected_language)


def render_data_science_tab(coding_assistant, selected_language: str, session_state) -> None:
    """Render the data science tab UI"""
    st.markdown("### 📊 Data Science & Machine Learning")
    st.markdown("Advanced data analysis, ML models, and visualizations with numpy, pandas, scikit-learn, and matplotlib")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Data Science task selection
        ds_task_type = st.selectbox(
            "**Data Science Task**",
            options=list(DATA_SCIENCE_EXAMPLES.keys()),
            help="Choose the type of data science task you want to accomplish"
        )
        
        # Task description
        ds_description = st.text_area(
            "**Task Description**",
            height=120,
            placeholder=f"Describe your data science task...\n\nExample: {DATA_SCIENCE_EXAMPLES.get(ds_task_type, 'Describe what you want to accomplish with your data')}",
            help="Provide details about your data and what you want to achieve"
        )
        
        # Dataset information
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            data_format = st.selectbox(
                "**Data Format**",
                ["CSV", "JSON", "Excel", "Database", "API", "Text", "Images", "Other"],
                help="What format is your data in?"
            )
            
            data_size = st.selectbox(
                "**Dataset Size**",
                ["Small (<1MB)", "Medium (1MB-100MB)", "Large (100MB-1GB)", "Very Large (>1GB)"],
                help="Approximate size of your dataset"
            )
        
        with col1_2:
            include_plots = st.checkbox("📈 Include Visualizations", value=True)
            include_stats = st.checkbox("📊 Statistical Summary", value=True)
            include_ml_metrics = st.checkbox("🎯 ML Performance Metrics", value=False)
            optimize_code = st.checkbox("⚡ Optimize for Performance", value=False)
        
        if st.button("🧬 Generate Data Science Code", type="primary"):
            if ds_description.strip():
                _handle_data_science_request(
                    session_state, ds_task_type, ds_description, data_format, data_size,
                    include_plots, include_stats, include_ml_metrics, optimize_code
                )
            else:
                st.warning("⚠️ Please provide a task description")
    
    with col2:
        _render_data_science_resources()


def render_chain_of_thought_tab(coding_assistant, selected_language: str, session_state) -> None:
    """Render the chain-of-thought reasoning tab UI"""
    st.markdown("### 🧠 Chain-of-Thought Reasoning")
    st.markdown("Advanced problem-solving with structured reasoning and step-by-step analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Reasoning configuration
        st.markdown("#### ⚙️ Reasoning Configuration")
        
        reasoning_enabled = st.checkbox(
            "🧠 Enable Chain-of-Thought Reasoning", 
            value=True,
            help="Use structured reasoning for complex problems"
        )
        
        # Reasoning type selection
        reasoning_types = {
            "Auto-detect": None,
            "Chain-of-Thought": ReasoningType.CHAIN_OF_THOUGHT,
            "ReAct (Reason + Act)": ReasoningType.REACT,
            "Step-by-Step": ReasoningType.STEP_BY_STEP,
            "Problem Decomposition": ReasoningType.PROBLEM_DECOMPOSITION,
            "Reflection": ReasoningType.REFLECTION
        }
        
        selected_reasoning = st.selectbox(
            "🎯 Reasoning Approach",
            options=list(reasoning_types.keys()),
            help="Choose how the AI should approach complex problems"
        )
        
        reasoning_type = reasoning_types[selected_reasoning]
        
        # Update agent settings
        if reasoning_enabled:
            session_state.coding_agent.enable_reasoning(True)
        else:
            session_state.coding_agent.enable_reasoning(False)
        
        # Problem input
        st.markdown("#### 🤔 Complex Problem Solving")
        
        problem_description = st.text_area(
            "**Problem Description**",
            height=150,
            placeholder="Describe a complex coding problem, algorithm challenge, system design question, or any technical issue that requires structured thinking...\n\nExample:\n- How to design a scalable microservices architecture?\n- Debug a performance issue in a large codebase\n- Implement a complex algorithm with optimal time complexity\n- Design a secure authentication system",
            help="Provide a detailed description of the problem you want to solve"
        )
        
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            show_reasoning_steps = st.checkbox("📋 Show Reasoning Steps", value=True)
            include_confidence = st.checkbox("📊 Include Confidence Scores", value=True)
        
        with col1_2:
            save_reasoning = st.checkbox("💾 Save Reasoning Chain", value=True)
            detailed_analysis = st.checkbox("🔍 Detailed Analysis", value=False)
        
        if st.button("🧠 Analyze with Chain-of-Thought", type="primary"):
            if problem_description.strip():
                _handle_chain_of_thought_analysis(
                    session_state, selected_language, problem_description, reasoning_enabled,
                    reasoning_type, selected_reasoning, show_reasoning_steps, include_confidence,
                    save_reasoning, detailed_analysis
                )
            else:
                st.warning("⚠️ Please provide a problem description")
    
    with col2:
        _render_reasoning_guidance(session_state)


# Helper functions for handling business logic
def _handle_code_generation(session_state, selected_language: str, template_type: str, 
                          description: str, include_tests: bool, include_docs: bool,
                          include_comments: bool, follow_conventions: bool) -> None:
    """Handle code generation request"""
    with st.spinner("🤖 Generating code..."):
        try:
            # Prepare detailed prompt
            prompt_parts = [f"Create {selected_language} code: {description}"]
            
            if include_tests:
                prompt_parts.append("Include comprehensive unit tests")
            if include_docs:
                prompt_parts.append("Include detailed documentation")
            if include_comments:
                prompt_parts.append("Add inline comments explaining the code")
            if follow_conventions:
                prompt_parts.append(f"Follow {selected_language} best practices and conventions")
            
            full_prompt = ". ".join(prompt_parts)
            
            response = session_state.coding_agent.chat_sync(
                full_prompt,
                session_state.coding_session_id
            )
            
            # Display result
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown("### 🎯 Generated Code")
            st.code(response, language=selected_language)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Save session
            session_data = SessionData(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                session_type='code_generation',
                language=selected_language,
                template=template_type,
                description=description,
                response=response,
                options={
                    'include_tests': include_tests,
                    'include_docs': include_docs,
                    'include_comments': include_comments,
                    'follow_conventions': follow_conventions
                }
            )
            
            session_state.coding_history.append(session_data.__dict__)
            
            st.success("✅ Code generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Error generating code: {str(e)}")
            logger.error(f"Code generation error: {str(e)}")


def _handle_code_review(session_state, selected_language: str, code_input: str, 
                       review_aspects: List[str]) -> None:
    """Handle code review request"""
    with st.spinner("🤖 Analyzing code..."):
        try:
            prompt = f"""Review this {selected_language} code and provide detailed analysis focusing on: {', '.join(review_aspects)}.

Code:
```{selected_language}
{code_input}
```

Please provide:
1. Overall assessment
2. Specific issues and improvements
3. Best practice recommendations
4. Refactored code suggestions if needed"""

            response = session_state.coding_agent.chat_sync(
                prompt,
                session_state.coding_session_id
            )
            
            # Display result
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown("### 🎯 Code Review Results")
            st.write(response)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Save session
            session_data = SessionData(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                session_type='code_review',
                language=selected_language,
                code=code_input,
                review_aspects=review_aspects,
                response=response
            )
            
            session_state.coding_history.append(session_data.__dict__)
            
            st.success("✅ Code review completed!")
            
        except Exception as e:
            st.error(f"❌ Error reviewing code: {str(e)}")
            logger.error(f"Code review error: {str(e)}")


def _handle_debug_code(session_state, selected_language: str, buggy_code: str,
                      error_message: str, expected_behavior: str) -> None:
    """Handle debug code request"""
    with st.spinner("🤖 Debugging code..."):
        try:
            prompt = f"""Debug this {selected_language} code and provide a solution.

Problematic Code:
```{selected_language}
{buggy_code}
```

Error Message: {error_message if error_message else 'No specific error message provided'}
Expected Behavior: {expected_behavior if expected_behavior else 'Not specified'}

Please provide:
1. Root cause analysis
2. Step-by-step explanation of the issue
3. Fixed code with corrections
4. Prevention tips for similar issues"""

            response = session_state.coding_agent.chat_sync(
                prompt,
                session_state.coding_session_id
            )
            
            # Display result
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown("### 🎯 Debug Results")
            st.write(response)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Save session
            session_data = SessionData(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                session_type='code_debug',
                language=selected_language,
                code=buggy_code,
                error_message=error_message,
                expected_behavior=expected_behavior,
                response=response
            )
            
            session_state.coding_history.append(session_data.__dict__)
            
            st.success("✅ Debugging completed!")
            
        except Exception as e:
            st.error(f"❌ Error debugging code: {str(e)}")
            logger.error(f"Debug error: {str(e)}")


def _get_learning_input(learning_type: str, selected_language: str) -> str:
    """Get input for learning requests based on type"""
    if learning_type == "Explain Code":
        return st.text_area(
            "**Code to Explain**",
            height=200,
            placeholder=f"Paste {selected_language} code to get a detailed explanation...",
        )
    elif learning_type == "Learn Concept":
        return st.text_input(
            "**Programming Concept**",
            placeholder="e.g., recursion, design patterns, algorithms...",
        )
    elif learning_type == "Compare Solutions":
        return st.text_input(
            "**What to Compare**",
            placeholder="e.g., 'list vs array', 'SQL vs NoSQL', 'REST vs GraphQL'...",
        )
    else:  # Best Practices
        return st.text_input(
            "**Practice Area**",
            placeholder="e.g., error handling, testing, security, performance...",
        )


def _handle_learning_request(session_state, selected_language: str, learning_type: str,
                           query_input: str) -> None:
    """Handle learning and explanation requests"""
    with st.spinner("🤖 Preparing explanation..."):
        try:
            if learning_type == "Explain Code":
                prompt = f"Explain this {selected_language} code in detail, including what it does, how it works, and any important concepts:\n\n```{selected_language}\n{query_input}\n```"
            elif learning_type == "Learn Concept":
                prompt = f"Explain the programming concept '{query_input}' with examples in {selected_language}. Include practical applications and best practices."
            elif learning_type == "Compare Solutions":
                prompt = f"Compare and contrast {query_input} in the context of {selected_language} programming. Explain pros, cons, and when to use each."
            else:  # Best Practices
                prompt = f"Explain best practices for {query_input} in {selected_language} programming. Include examples and common pitfalls to avoid."
            
            response = session_state.coding_agent.chat_sync(
                prompt,
                session_state.coding_session_id
            )
            
            # Display result
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown("### 🎯 Explanation")
            st.write(response)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Save session
            session_data = SessionData(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                session_type='learning',
                language=selected_language,
                learning_type=learning_type,
                query=query_input,
                response=response
            )
            
            session_state.coding_history.append(session_data.__dict__)
            
            st.success("✅ Explanation provided!")
            
        except Exception as e:
            st.error(f"❌ Error getting explanation: {str(e)}")
            logger.error(f"Learning error: {str(e)}")


def _handle_data_science_request(session_state, ds_task_type: str, ds_description: str,
                               data_format: str, data_size: str, include_plots: bool,
                               include_stats: bool, include_ml_metrics: bool,
                               optimize_code: bool) -> None:
    """Handle data science code generation requests"""
    with st.spinner("🤖 Creating data science solution..."):
        try:
            # Prepare comprehensive data science prompt
            prompt_parts = [
                f"Create Python code for {ds_task_type.lower()}: {ds_description}",
                f"Data format: {data_format}",
                f"Dataset size: {data_size}",
                "Use appropriate libraries: numpy, pandas, scikit-learn, matplotlib"
            ]
            
            if include_plots:
                prompt_parts.append("Include matplotlib visualizations with proper labels and styling")
            if include_stats:
                prompt_parts.append("Include statistical analysis and summary statistics")
            if include_ml_metrics and "Model" in ds_task_type:
                prompt_parts.append("Include comprehensive model evaluation metrics")
            if optimize_code:
                prompt_parts.append("Optimize code for performance and memory efficiency")
            
            prompt_parts.extend([
                "Include error handling and data validation",
                "Add detailed comments explaining each step",
                "Follow data science best practices",
                "Make the code production-ready and well-structured"
            ])
            
            full_prompt = ". ".join(prompt_parts)
            
            response = session_state.coding_agent.chat_sync(
                full_prompt,
                session_state.coding_session_id
            )
            
            # Display result
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown("### 🎯 Data Science Code")
            st.code(response, language="python")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Save session
            session_data = SessionData(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                session_type='data_science',
                task_type=ds_task_type,
                description=ds_description,
                data_format=data_format,
                data_size=data_size,
                response=response,
                options={
                    'include_plots': include_plots,
                    'include_stats': include_stats,
                    'include_ml_metrics': include_ml_metrics,
                    'optimize_code': optimize_code
                }
            )
            
            session_state.coding_history.append(session_data.__dict__)
            
            st.success("✅ Data science code generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Error generating data science code: {str(e)}")
            logger.error(f"Data science code generation error: {str(e)}")


def _handle_chain_of_thought_analysis(session_state, selected_language: str, problem_description: str,
                                    reasoning_enabled: bool, reasoning_type, selected_reasoning: str,
                                    show_reasoning_steps: bool, include_confidence: bool,
                                    save_reasoning: bool, detailed_analysis: bool) -> None:
    """Handle chain-of-thought reasoning analysis"""
    with st.spinner("🤖 Thinking step by step..."):
        try:
            # Check if reasoning should be used
            if reasoning_enabled:
                response, reasoning_chain = session_state.coding_agent.chat_sync_with_reasoning(
                    problem_description,
                    session_state.coding_session_id,
                    use_cot=True,
                    reasoning_type=reasoning_type
                )
            else:
                response = session_state.coding_agent.chat_sync(
                    problem_description,
                    session_state.coding_session_id
                )
                reasoning_chain = None
            
            # Display result
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown("### 🎯 AI Analysis")
            
            if reasoning_chain and show_reasoning_steps:
                st.markdown("#### 🔄 Reasoning Process")
                
                for i, step in enumerate(reasoning_chain.steps):
                    with st.expander(f"Step {step.step_number}: {step.thought[:50]}..."):
                        st.markdown(f"**Thought:** {step.thought}")
                        if step.action:
                            st.markdown(f"**Action:** {step.action}")
                        if step.observation:
                            st.markdown(f"**Observation:** {step.observation}")
                        if include_confidence:
                            st.progress(step.confidence)
                            st.caption(f"Confidence: {step.confidence:.1%}")
                
                if include_confidence and reasoning_chain.confidence_score > 0:
                    st.markdown("#### 📊 Overall Confidence")
                    st.progress(reasoning_chain.confidence_score)
                    st.caption(f"Overall confidence: {reasoning_chain.confidence_score:.1%}")
            
            st.markdown("#### 💡 Final Response")
            st.write(response)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Save session
            if save_reasoning:
                session_data = SessionData(
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    session_type='chain_of_thought',
                    language=selected_language,
                    problem=problem_description,
                    response=response,
                    reasoning_enabled=reasoning_enabled,
                    reasoning_type=selected_reasoning,
                    reasoning_chain={
                        'steps_count': len(reasoning_chain.steps) if reasoning_chain else 0,
                        'confidence_score': reasoning_chain.confidence_score if reasoning_chain else 0,
                        'reasoning_type': reasoning_chain.reasoning_type.value if reasoning_chain else None
                    } if reasoning_chain else None
                )
                
                session_state.coding_history.append(session_data.__dict__)
            
            st.success("✅ Chain-of-Thought analysis completed!")
            
        except Exception as e:
            st.error(f"❌ Error in reasoning analysis: {str(e)}")
            logger.error(f"Chain-of-Thought error: {str(e)}")


# UI Component Helpers
def _render_generation_tips() -> None:
    """Render generation tips sidebar"""
    st.markdown("### 💡 Generation Tips")
    
    st.markdown("""
    <div class="feature-card">
        <h4>🎯 Be Specific</h4>
        <p>Provide detailed requirements and constraints</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h4>📊 Include Examples</h4>
        <p>Mention input/output examples if applicable</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h4>⚡ Performance Needs</h4>
        <p>Specify performance requirements</p>
    </div>
    """, unsafe_allow_html=True)


def _render_review_guidelines() -> None:
    """Render review guidelines sidebar"""
    st.markdown("### 📋 Review Guidelines")
    
    for aspect in REVIEW_ASPECTS:
        st.markdown(f"""
        <div class="feature-card">
            <h5>✓ {aspect}</h5>
        </div>
        """, unsafe_allow_html=True)


def _render_debug_tips() -> None:
    """Render debug tips sidebar"""
    st.markdown("### 🔧 Debug Tips")
    
    st.markdown("""
    <div class="feature-card">
        <h4>📍 Provide Context</h4>
        <p>Include relevant code context and environment</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h4>🔍 Include Error Details</h4>
        <p>Copy full error messages and stack traces</p>
    </div>
    """, unsafe_allow_html=True)


def _render_learning_resources(selected_language: str) -> None:
    """Render learning resources sidebar"""
    st.markdown("### 🎓 Learning Resources")
    
    lang_info = get_language_info(selected_language)
    st.markdown(f"""
    <div class="feature-card">
        <h4>{lang_info['icon']} {selected_language.title()}</h4>
        <p>Current focus language</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h4>💡 Ask Questions</h4>
        <p>Don't hesitate to ask for clarification</p>
    </div>
    """, unsafe_allow_html=True)


def _render_data_science_resources() -> None:
    """Render data science resources sidebar"""
    st.markdown("### 🧰 Available Libraries")
    
    libraries = [
        ("🔢 NumPy", "Numerical computing and array operations"),
        ("🐼 Pandas", "Data manipulation and analysis"),
        ("🤖 Scikit-learn", "Machine learning algorithms and tools"),
        ("📈 Matplotlib", "Data visualization and plotting")
    ]
    
    for lib_name, lib_desc in libraries:
        st.markdown(f"""
        <div class="feature-card">
            <h4>{lib_name}</h4>
            <p>{lib_desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 💡 Quick Tips")
    
    tips = [
        ("📋 Data Format", "Always specify your data format and structure"),
        ("🎯 Clear Goals", "Define what insights or predictions you need")
    ]
    
    for tip_title, tip_desc in tips:
        st.markdown(f"""
        <div class="feature-card">
            <h4>{tip_title}</h4>
            <p>{tip_desc}</p>
        </div>
        """, unsafe_allow_html=True)


def _render_reasoning_guidance(session_state) -> None:
    """Render reasoning guidance and statistics sidebar"""
    st.markdown("### 🎓 Reasoning Types")
    
    reasoning_types = [
        ("🔗 Chain-of-Thought", "Step-by-step logical reasoning through complex problems"),
        ("⚡ ReAct", "Combines reasoning with actions and observations"),
        ("📋 Step-by-Step", "Structured procedural approach to problems"),
        ("🧩 Decomposition", "Break complex problems into manageable parts"),
        ("🪞 Reflection", "Analyze problems through multiple perspectives")
    ]
    
    for reasoning_name, reasoning_desc in reasoning_types:
        st.markdown(f"""
        <div class="feature-card">
            <h4>{reasoning_name}</h4>
            <p>{reasoning_desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Reasoning history
    reasoning_history = session_state.coding_agent.get_reasoning_history()
    if reasoning_history:
        st.markdown("### 📊 Reasoning Statistics")
        
        total_chains = len(reasoning_history)
        avg_confidence = sum(chain.confidence_score for chain in reasoning_history) / total_chains if total_chains > 0 else 0
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Total Analyses", total_chains)
        with col_stat2:
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
        
        if st.button("📥 Export Reasoning Analysis"):
            analysis = session_state.coding_agent.export_reasoning_analysis()
            st.download_button(
                label="Download Analysis",
                data=json.dumps(analysis, indent=2),
                file_name=f"reasoning_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
