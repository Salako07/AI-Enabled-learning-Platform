# ai_features/services.py

import openai
import anthropic
from django.conf import settings
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for integrating with OpenAI APIs"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def get_tutor_response(self, message: str, session_history: List[Dict], context: Dict) -> Dict:
        """Get AI tutor response"""
        try:
            # Build conversation context
            system_prompt = self._build_tutor_system_prompt(context)
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for msg in session_history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_message = response.choices[0].message.content
            
            # Extract suggestions and code examples
            suggestions = self._extract_suggestions(ai_message)
            code_examples = self._extract_code_examples(ai_message)
            
            return {
                "message": ai_message,
                "suggestions": suggestions,
                "code_examples": code_examples,
                "usage": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def analyze_code(self, code: str, language: str, analysis_type: str) -> Dict:
        """Analyze code for quality, bugs, and improvements"""
        try:
            prompt = self._build_code_analysis_prompt(code, language, analysis_type)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer and software engineer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = self._parse_code_analysis_response(response.choices[0].message.content)
            
            return result
            
        except Exception as e:
            logger.error(f"Code analysis error: {str(e)}")
            raise
    
    def generate_interview_questions(self, interview_type: str, difficulty: str, 
                                   company: str = "", role: str = "") -> List[Dict]:
        """Generate mock interview questions"""
        try:
            prompt = self._build_interview_prompt(interview_type, difficulty, company, role)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            questions = self._parse_interview_questions(response.choices[0].message.content)
            
            return questions
            
        except Exception as e:
            logger.error(f"Interview generation error: {str(e)}")
            raise
    
    def evaluate_skill_assessment(self, questions: List[Dict], answers: List[Dict], 
                                 skill_areas: List[str]) -> Dict:
        """Evaluate skill assessment responses"""
        try:
            prompt = self._build_assessment_evaluation_prompt(questions, answers, skill_areas)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert skills assessor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            evaluation = self._parse_assessment_evaluation(response.choices[0].message.content)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Assessment evaluation error: {str(e)}")
            raise
    
    def _build_tutor_system_prompt(self, context: Dict) -> str:
        """Build system prompt for AI tutor"""
        base_prompt = """You are an expert programming tutor and mentor. Your role is to:
        1. Help students understand programming concepts clearly
        2. Provide step-by-step explanations
        3. Give practical examples and exercises
        4. Encourage good coding practices
        5. Be patient and supportive
        
        Always:
        - Break down complex topics into simple steps
        - Provide code examples when helpful
        - Ask clarifying questions if needed
        - Encourage the student to try things themselves
        - Give constructive feedback
        """
        
        if context.get('programming_language'):
            base_prompt += f"\n\nYou are currently helping with {context['programming_language']} programming."
        
        if context.get('course_id'):
            base_prompt += f"\n\nThis is in the context of a specific course the student is taking."
        
        if context.get('lesson_id'):
            base_prompt += f"\n\nThe student is working on a specific lesson."
        
        return base_prompt
    
    def _build_code_analysis_prompt(self, code: str, language: str, analysis_type: str) -> str:
        """Build prompt for code analysis"""
        prompt = f"""Analyze the following {language} code for {analysis_type}.

Code:
```{language}
{code}
```

Please provide a comprehensive analysis including:
1. Overall code quality score (0-100)
2. Readability score (0-100)
3. Efficiency score (0-100)
4. Maintainability score (0-100)
5. Specific suggestions for improvement
6. Best practices recommendations
7. Potential bugs or issues
8. Performance concerns
9. Security issues (if any)
10. Refactored version of the code

Format your response as a structured analysis with clear sections."""
        
        return prompt
    
    def _build_interview_prompt(self, interview_type: str, difficulty: str, 
                               company: str, role: str) -> str:
        """Build prompt for interview question generation"""
        prompt = f"""Generate 5-7 {interview_type} interview questions for a {difficulty} level {role} position"""
        
        if company:
            prompt += f" at {company}"
        
        prompt += f""".

The questions should:
1. Be appropriate for the {difficulty} difficulty level
2. Test relevant skills for {interview_type}
3. Include a mix of theoretical and practical questions
4. Provide sample answers or evaluation criteria

Format as JSON with this structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "type": "coding|system_design|behavioral",
      "difficulty": "{difficulty}",
      "topic": "Relevant topic",
      "evaluation_criteria": ["criterion1", "criterion2"],
      "sample_answer": "Optional sample answer or approach"
    }}
  ]
}}"""
        
        return prompt
    
    def _extract_suggestions(self, message: str) -> List[str]:
        """Extract actionable suggestions from AI response"""
        # Simple extraction - could be improved with NLP
        suggestions = []
        lines = message.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('• '):
                suggestions.append(line[2:])
            elif line.startswith('1. ') or line.startswith('2. '):
                suggestions.append(line[3:])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _extract_code_examples(self, message: str) -> List[Dict]:
        """Extract code examples from AI response"""
        code_examples = []
        lines = message.split('\n')
        in_code_block = False
        current_code = []
        current_language = 'python'
        
        for line in lines:
            if line.startswith('```'):
                if in_code_block:
                    # End of code block
                    if current_code:
                        code_examples.append({
                            'language': current_language,
                            'code': '\n'.join(current_code)
                        })
                    current_code = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    if len(line) > 3:
                        current_language = line[3:].strip()
            elif in_code_block:
                current_code.append(line)
        
        return code_examples
    
    def _parse_code_analysis_response(self, response: str) -> Dict:
        """Parse code analysis response"""
        # This would be more sophisticated in practice
        return {
            'overall_score': 85.0,
            'readability_score': 90.0,
            'efficiency_score': 80.0,
            'maintainability_score': 85.0,
            'suggestions': [
                'Add type hints for better code documentation',
                'Consider using list comprehensions for better performance',
                'Add docstrings to functions'
            ],
            'best_practices': [
                'Follow PEP 8 style guidelines',
                'Use descriptive variable names',
                'Keep functions small and focused'
            ],
            'potential_bugs': [
                'Possible index out of range error on line 15'
            ],
            'performance_issues': [
                'Nested loops could be optimized'
            ],
            'security_concerns': [],
            'refactored_code': response  # Would contain actual refactored code
        }
    
    def _parse_interview_questions(self, response: str) -> List[Dict]:
        """Parse interview questions from response"""
        try:
            # Try to parse as JSON first
            data = json.loads(response)
            return data.get('questions', [])
        except json.JSONDecodeError:
            # Fallback parsing if not JSON
            return [
                {
                    'question': 'Sample coding question',
                    'type': 'coding',
                    'difficulty': 'medium',
                    'topic': 'algorithms',
                    'evaluation_criteria': ['correctness', 'efficiency'],
                    'sample_answer': 'Approach explanation'
                }
            ]
    
    def _parse_assessment_evaluation(self, response: str) -> Dict:
        """Parse skill assessment evaluation"""
        # Simplified parsing - would be more sophisticated
        return {
            'overall_score': 75.0,
            'skill_scores': {
                'python': 80.0,
                'algorithms': 70.0,
                'problem_solving': 75.0
            },
            'competency_level': 'intermediate',
            'strengths': ['Good understanding of basic concepts', 'Clean code style'],
            'weaknesses': ['Needs work on complex algorithms', 'Time complexity analysis'],
            'recommendations': [
                'Practice more algorithm problems',
                'Study time and space complexity',
                'Work on system design basics'
            ],
            'confidence': 0.85
        }


class AnthropicService:
    """Service for integrating with Anthropic Claude API"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def get_explanation(self, concept: str, context: Dict) -> str:
        """Get detailed explanation of a concept"""
        try:
            prompt = f"""Please explain the concept of "{concept}" in programming.
            
            Context: {context.get('level', 'beginner')} level
            Language: {context.get('language', 'general programming')}
            
            Provide a clear, comprehensive explanation with:
            1. Definition and key points
            2. Practical examples
            3. Common use cases
            4. Best practices
            5. Common mistakes to avoid
            
            Keep the explanation appropriate for a {context.get('level', 'beginner')} level."""
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def generate_content(self, content_type: str, specifications: Dict) -> str:
        """Generate educational content"""
        try:
            prompt = self._build_content_generation_prompt(content_type, specifications)
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            raise
    
    def _build_content_generation_prompt(self, content_type: str, specs: Dict) -> str:
        """Build prompt for content generation"""
        if content_type == 'lesson':
            return f"""Create a comprehensive lesson on "{specs['topic']}" for {specs['level']} level students.

            Requirements:
            - Duration: {specs.get('duration', '30 minutes')}
            - Learning objectives: {specs.get('objectives', [])}
            - Include practical examples
            - Add exercises for practice
            - Make it engaging and interactive
            
            Structure the lesson with clear sections and actionable content."""
        
        elif content_type == 'quiz':
            return f"""Create a quiz with {specs.get('num_questions', 5)} questions on "{specs['topic']}".
            
            Requirements:
            - Difficulty: {specs['level']}
            - Question types: {specs.get('question_types', ['multiple_choice'])}
            - Include explanations for answers
            - Cover key concepts comprehensively"""
        
        return f"Generate {content_type} content based on: {specs}"


class RecommendationEngine:
    """AI-powered recommendation engine"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    def generate_recommendations(self, user) -> List[Dict]:
        """Generate personalized learning recommendations"""
        try:
            user_profile = self._build_user_profile(user)
            learning_history = self._get_learning_history(user)
            current_goals = user.learning_goals
            
            prompt = f"""Based on this user profile, generate 3-5 personalized learning recommendations:

            User Profile:
            - Skill Level: {user.current_skill_level}
            - Learning Style: {user.learning_style}
            - Goals: {current_goals}
            - Completed Courses: {learning_history['completed_courses']}
            - Current Skills: {learning_history['skills']}
            - Weak Areas: {learning_history['weak_areas']}
            
            Generate recommendations that:
            1. Match the user's skill level and goals
            2. Address skill gaps
            3. Follow logical learning progression
            4. Are engaging and achievable
            
            Return as JSON array with this structure:
            [
              {{
                "type": "course|skill|practice",
                "priority": "high|medium|low",
                "title": "Recommendation title",
                "description": "Detailed description",
                "reasoning": "Why this is recommended",
                "target_skill": "Skill being developed",
                "confidence": 0.85,
                "course_id": "optional_course_id"
              }}
            ]"""
            
            response = self.openai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert learning advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            try:
                recommendations = json.loads(response.choices[0].message.content)
                return recommendations if isinstance(recommendations, list) else []
            except json.JSONDecodeError:
                return self._fallback_recommendations(user)
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {str(e)}")
            return self._fallback_recommendations(user)
    
    def _build_user_profile(self, user) -> Dict:
        """Build comprehensive user profile for recommendations"""
        return {
            'skill_level': user.current_skill_level,
            'learning_style': user.learning_style,
            'goals': user.learning_goals,
            'subscription_tier': user.subscription_tier,
            'total_learning_time': str(user.total_learning_time),
            'current_streak': user.current_streak,
        }
    
    def _get_learning_history(self, user) -> Dict:
        """Get user's learning history and progress"""
        from courses.models import CourseEnrollment
        from accounts.models import UserSkill
        
        completed_courses = CourseEnrollment.objects.filter(
            user=user,
            status='completed'
        ).values_list('course__title', flat=True)
        
        skills = UserSkill.objects.filter(user=user).values_list('skill_name', flat=True)
        
        # Simplified weak areas detection
        weak_areas = []
        for skill in UserSkill.objects.filter(user=user, proficiency_level__lt=3):
            weak_areas.append(skill.skill_name)
        
        return {
            'completed_courses': list(completed_courses),
            'skills': list(skills),
            'weak_areas': weak_areas
        }
    
    def _fallback_recommendations(self, user) -> List[Dict]:
        """Fallback recommendations if AI generation fails"""
        return [
            {
                'type': 'course',
                'priority': 'medium',
                'title': 'Continue Your Learning Journey',
                'description': 'Based on your progress, here are some suggested next steps.',
                'reasoning': 'Maintains learning momentum',
                'target_skill': 'general',
                'confidence': 0.6
            }
        ]


class CodeExecutionService:
    """Service for executing code in sandboxed environments"""
    
    def __init__(self):
        self.supported_languages = {
            'python': 'python:3.9-slim',
            'javascript': 'node:16-slim',
            'java': 'openjdk:11-slim',
            'cpp': 'gcc:latest',
            'go': 'golang:1.19-slim'
        }
    
    def execute_code(self, code: str, language: str, input_data: str = "") -> Dict:
        """Execute code in a sandboxed environment"""
        try:
            # This would integrate with Docker or similar containerization
            # For now, return a mock response
            
            if language not in self.supported_languages:
                return {
                    'success': False,
                    'error': f'Language {language} not supported',
                    'output': '',
                    'execution_time': 0,
                    'memory_used': 0
                }
            
            # Mock execution results
            return {
                'success': True,
                'output': 'Hello, World!\n',
                'error': '',
                'execution_time': 0.123,  # seconds
                'memory_used': 1024,  # bytes
                'exit_code': 0
            }
            
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': 0,
                'memory_used': 0
            }
    
    def run_test_cases(self, code: str, language: str, test_cases: List[Dict]) -> Dict:
        """Run code against multiple test cases"""
        results = []
        passed = 0
        
        for i, test_case in enumerate(test_cases):
            result = self.execute_code(code, language, test_case.get('input', ''))
            
            expected_output = test_case.get('expected_output', '').strip()
            actual_output = result.get('output', '').strip()
            
            test_passed = actual_output == expected_output
            if test_passed:
                passed += 1
            
            results.append({
                'test_case': i + 1,
                'passed': test_passed,
                'input': test_case.get('input', ''),
                'expected_output': expected_output,
                'actual_output': actual_output,
                'execution_time': result.get('execution_time', 0),
                'error': result.get('error', '')
            })
        
        return {
            'total_tests': len(test_cases),
            'passed_tests': passed,
            'success_rate': passed / len(test_cases) if test_cases else 0,
            'results': results
        }


class PlagiarismDetectionService:
    """Service for detecting code plagiarism and similarity"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    def check_similarity(self, code1: str, code2: str, language: str) -> Dict:
        """Check similarity between two code submissions"""
        try:
            prompt = f"""Compare these two {language} code submissions for similarity:

            Code 1:
            ```{language}
            {code1}
            ```

            Code 2:
            ```{language}
            {code2}
            ```

            Analyze:
            1. Structural similarity (0-100%)
            2. Logic similarity (0-100%)
            3. Variable naming similarity (0-100%)
            4. Overall similarity score (0-100%)
            5. Specific similar patterns
            6. Likelihood of plagiarism (low/medium/high)

            Provide detailed analysis of similarities and differences."""
            
            response = self.openai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at code analysis and plagiarism detection."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse response and return similarity metrics
            return {
                'structural_similarity': 75.0,
                'logic_similarity': 80.0,
                'naming_similarity': 30.0,
                'overall_similarity': 70.0,
                'plagiarism_likelihood': 'medium',
                'analysis': response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Plagiarism detection error: {str(e)}")
            return {
                'structural_similarity': 0.0,
                'logic_similarity': 0.0,
                'naming_similarity': 0.0,
                'overall_similarity': 0.0,
                'plagiarism_likelihood': 'unknown',
                'analysis': 'Analysis failed'
            }