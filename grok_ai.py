import os
from groq import Groq
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

class GrokAI:
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        if not self.api_key:
            raise ValueError("GROK_API_KEY not found in environment variables. Please add it to your .env file.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"  # Updated to current model
    
    def generate_title(self, video_analysis, custom_prompt=None):
        """Generate an engaging YouTube title based on video analysis"""
        
        base_prompt = f"""
You are a YouTube SEO expert specializing in creating viral, engaging titles. Based on the detailed video analysis below, create a compelling YouTube title that matches the ACTUAL CONTENT of the video.

IMPORTANT: Use the video analysis to understand what the video is REALLY about, then create a title that accurately reflects that content while being engaging.

{video_analysis}

Additional Context: {custom_prompt if custom_prompt else "No additional context provided."}

Create a title that:
1. ACCURATELY reflects the video content based on the analysis above
2. Is 40-100 characters long
3. Uses engaging language and power words
4. Creates curiosity without misleading
5. Includes relevant keywords for the content type
6. Matches the video's actual pacing and style

Examples of good titles for different content types:
- Tutorial/Presentation: "Master [Skill] in [Time] - Step-by-Step Guide"  
- Entertainment/Dynamic: "[Number] [Adjective] [Things] That Will [Action]"
- Interview/Talking: "[Person] Reveals [Secret/Truth] About [Topic]"

Generate 3 title options and select the best one. Format as JSON:
{{
    "options": ["title1", "title2", "title3"],
    "selected": "best_title_here",
    "reasoning": "why this title matches the video content and will perform well"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": base_prompt}],
                temperature=0.8,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                result = json.loads(content)
                return {
                    'title': result['selected'],
                    'options': result.get('options', []),
                    'reasoning': result.get('reasoning', '')
                }
            except json.JSONDecodeError:
                # Fallback: extract title from text - look for actual title content
                lines = content.strip().split('\n')
                best_title = None
                
                # Look for lines that could be titles (reasonable length, no colons at start)
                for line in lines:
                    clean_line = line.strip().strip('"\'').strip()
                    if (clean_line and 
                        20 <= len(clean_line) <= 100 and 
                        not clean_line.startswith('{') and
                        not clean_line.startswith('JSON') and
                        not clean_line.lower().startswith('here') and
                        ':' not in clean_line[:10]):
                        best_title = clean_line
                        break
                
                if not best_title:
                    # Extract from anywhere in the text
                    words = content.split()
                    if len(words) >= 5:
                        best_title = ' '.join(words[:10])  # Take first 10 words
                    else:
                        best_title = "Amazing Video Content"
                
                return {
                    'title': best_title[:100], 
                    'options': [best_title], 
                    'reasoning': 'Extracted from AI response'
                }
                
        except Exception as e:
            print(f"Error generating title: {e}")
            return {'title': 'Awesome Video Content', 'options': [], 'reasoning': 'Error occurred'}
    
    def generate_description(self, video_analysis, title, custom_prompt=None):
        """Generate a comprehensive YouTube description"""
        
        base_prompt = f"""
You are a YouTube content expert. Create a comprehensive, engaging video description based on the ACTUAL video content analysis provided.

DETAILED VIDEO ANALYSIS:
{video_analysis}

Title: {title}
Additional Context: {custom_prompt if custom_prompt else "No additional context provided."}

Write a description that:
1. MATCHES the actual video content based on the analysis above
2. Starts with a compelling hook that relates to the video's content type
3. Describes what viewers will actually see/learn based on the analysis
4. Uses natural keywords that match the content type and style
5. Is 200-800 words long
6. Includes clear structure with paragraphs

Content-specific guidelines:
- If it's a tutorial/presentation: Focus on what skills/knowledge viewers gain
- If it's entertainment/dynamic: Highlight the exciting moments and variety
- If it's interview/talking: Mention the insights and conversation topics
- If it's documentary/narrative: Describe the story and information covered

Structure:
- Hook (relate to the video's actual content and style)
- What the video covers (based on motion level, complexity, and content type)
- Key benefits/entertainment value for viewers
- Call to action (like, subscribe, comment)
- Relevant hashtags (3-5 based on content analysis)

Write in an engaging, natural tone that matches the video's style and pacing.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": base_prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            description = response.choices[0].message.content.strip()
            
            # Clean up the description - remove any leading instruction text
            lines = description.split('\n')
            cleaned_lines = []
            
            skip_until_content = True
            for line in lines:
                line = line.strip()
                # Skip intro text about being a YouTube expert, etc.
                if skip_until_content:
                    if (line and 
                        not line.lower().startswith('you are') and
                        not line.lower().startswith('create') and
                        not line.lower().startswith('based on') and
                        len(line) > 20):
                        skip_until_content = False
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            
            if cleaned_lines:
                description = '\n'.join(cleaned_lines)
            
            # Remove markdown formatting
            description = re.sub(r'\*\*', '', description)  # Remove markdown bold
            description = re.sub(r'\n{3,}', '\n\n', description)  # Limit line breaks
            description = description[:4000]  # YouTube description limit
            
            return description
            
        except Exception as e:
            print(f"Error generating description: {e}")
            return f"Check out this amazing video content!\n\n{title}\n\nDon't forget to like and subscribe for more great content!"
    
    def generate_thumbnail_concept(self, video_analysis, title):
        """Generate a concept for thumbnail design"""
        
        prompt = f"""
Based on this video analysis and title, create a thumbnail concept:

Title: {title}
Video Analysis: {video_analysis}

Describe a compelling YouTube thumbnail concept that:
1. Complements the title
2. Uses vibrant, contrasting colors
3. Includes text overlays if needed
4. Considers the video's visual style
5. Appeals to the target audience
6. Follows YouTube thumbnail best practices

Provide a detailed description of:
- Main visual elements
- Color scheme
- Text elements (if any)
- Overall composition
- Emotional tone

Keep it concise and actionable for thumbnail creation.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating thumbnail concept: {e}")
            return "Create a vibrant thumbnail with the main subject prominently displayed and complementary colors."
    
    def generate_tags(self, title, description, video_analysis):
        """Generate relevant tags for the video"""
        
        prompt = f"""
Generate 15-20 relevant YouTube tags based on:

Title: {title}
Description: {description[:300]}...
Video Analysis: {video_analysis}

Tags should be:
1. Relevant to the content
2. Mix of broad and specific terms
3. Include trending keywords where appropriate
4. Help with discoverability
5. Avoid tag stuffing

Return as a comma-separated list of tags.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=300
            )
            
            tags_text = response.choices[0].message.content.strip()
            
            # Clean and format tags - handle different response formats
            if ',' in tags_text:
                # Comma-separated format
                tags = [tag.strip().strip('"\'').strip() for tag in tags_text.split(',')]
            else:
                # Line-by-line or space-separated format
                words = tags_text.replace('\n', ' ').split()
                tags = []
                current_tag = ""
                
                for word in words:
                    word = word.strip().strip('"\'').strip(',').strip()
                    if word and not word.startswith('#'):
                        if len(current_tag + ' ' + word) <= 30:  # YouTube tag limit
                            current_tag = (current_tag + ' ' + word).strip()
                        else:
                            if current_tag:
                                tags.append(current_tag)
                            current_tag = word
                
                if current_tag:
                    tags.append(current_tag)
            
            # Filter and clean tags
            cleaned_tags = []
            for tag in tags:
                clean_tag = re.sub(r'^\d+\.?\s*', '', tag)  # Remove numbering
                clean_tag = clean_tag.strip().strip('"\'').strip()
                if (clean_tag and 
                    len(clean_tag) > 1 and 
                    len(clean_tag) <= 30 and
                    not clean_tag.lower().startswith('here') and
                    not clean_tag.lower().startswith('tags')):
                    cleaned_tags.append(clean_tag)
            
            return cleaned_tags[:15]  # Limit to 15 tags
            
        except Exception as e:
            print(f"Error generating tags: {e}")
            return ['video', 'content', 'youtube', 'awesome']