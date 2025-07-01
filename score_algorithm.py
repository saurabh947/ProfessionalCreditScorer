import google.generativeai as genai
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from database import DatabaseManager
from config import Config

class ProfessionalCreditScorer:
    """Professional Credit Scoring Algorithm using Google Gemini AI"""
    
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        self.db_manager = DatabaseManager()
        
        # Custom timeout settings for large datasets
        self.timeout_seconds = 300  # 5 minutes timeout
        self.max_retries = 3
        self.chunk_size = 1000  # Process in chunks if dataset is very large
        
        # Define the custom prompt for the credit scoring AI
        self.credit_scoring_prompt = """
        You are an advanced professional credit scoring AI system. Your role is to analyze 
        professional data and provide comprehensive credit scoring insights.

        CREDIT SCORING OBJECTIVES:
        1. Analyze professional work experience patterns
        2. Calculate average years of experience across all professionals
        3. Identify career progression indicators
        4. Assess professional stability and growth potential
        5. Provide detailed statistical analysis of the professional database

        ANALYSIS REQUIREMENTS:
        - Read and process all professional data from the database
        - Extract work experience information from the 'experience' field
        - Calculate total years of experience for each professional
        - Identify job transitions, promotions, and career stability
        - Analyze industry distribution and role diversity
        - Calculate average years of experience across the entire dataset
        - Identify experience patterns by industry, role level, and location

        DATA PROCESSING GUIDELINES:
        - Parse experience duration strings (e.g., "2 years 3 months", "1 year", "6 months")
        - Handle missing or incomplete experience data appropriately
        - Consider current position and historical positions
        - Account for overlapping employment periods
        - Calculate cumulative experience accurately

        OUTPUT FORMAT:
        Provide your analysis in the following JSON structure:
        {
            "analysis_summary": {
                "total_professionals_analyzed": <number>,
                "professionals_with_experience_data": <number>,
                "average_years_experience": <float>,
                "median_years_experience": <float>,
                "experience_range": {
                    "minimum": <float>,
                    "maximum": <float>
                }
            },
            "experience_distribution": {
                "entry_level_0_2_years": <number>,
                "mid_level_3_7_years": <number>,
                "senior_level_8_15_years": <number>,
                "executive_level_15_plus_years": <number>
            },
            "career_insights": {
                "average_job_tenure": <float>,
                "career_progression_rate": <float>,
                "industry_stability_score": <float>
            },
            "detailed_analysis": "<detailed_text_analysis>"
        }

        IMPORTANT: Focus on accurate calculation of years of experience and provide comprehensive 
        statistical analysis. Be thorough in your data processing and provide actionable insights 
        for credit scoring purposes.
        """
    
    def analyze_professional_database(self) -> Dict:
        """
        Analyze all professionals in the database using Gemini AI in batches
        Returns comprehensive credit scoring analysis
        """
        try:
            print("🔍 Starting professional database analysis for credit scoring...")
            
            # Get all professionals from database
            professionals = self.db_manager.get_all_professionals()
            
            if not professionals:
                print("❌ No professionals found in database")
                return self._create_empty_analysis()
            
            print(f"✅ Retrieved {len(professionals)} professionals from database")
            
            # Process in batches
            batch_size = 75
            total_batches = (len(professionals) + batch_size - 1) // batch_size
            all_results = []
            
            print(f"📊 Processing {len(professionals)} professionals in {total_batches} batches of {batch_size}")
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(professionals))
                batch_professionals = professionals[start_idx:end_idx]
                
                print(f"\n🔄 Processing batch {batch_num + 1}/{total_batches} (profiles {start_idx + 1}-{end_idx})")
                
                # Send batch to Gemini for analysis
                batch_result = self._analyze_batch(batch_professionals, batch_num + 1, total_batches)
                
                if batch_result:
                    all_results.append(batch_result)
                    print(f"✅ Batch {batch_num + 1} analysis completed successfully")
                else:
                    print(f"❌ Batch {batch_num + 1} analysis failed")
                
                # 60-second break between requests (except for the last batch)
                if batch_num < total_batches - 1:
                    print(f"⏰ Waiting 60 seconds before next batch...")
                    import time
                    time.sleep(60)
            
            # Aggregate all batch results
            if all_results:
                final_result = self._aggregate_batch_results(all_results, len(professionals))
                print("✅ Professional credit scoring analysis completed successfully")
                return final_result
            else:
                print("❌ All batch analyses failed")
                return self._create_empty_analysis()
                
        except Exception as e:
            print(f"❌ Error during professional analysis: {e}")
            return self._create_empty_analysis()
    
    def _analyze_batch(self, batch_professionals: List[Dict], batch_num: int, total_batches: int) -> Optional[Dict]:
        """Analyze a single batch of professionals"""
        try:
            # Prepare data for Gemini analysis
            analysis_prompt = self._prepare_analysis_prompt(batch_professionals, batch_num, total_batches)
            
            # Send to Gemini for analysis
            analysis_result = self._get_gemini_analysis(analysis_prompt)
            
            if analysis_result:
                # Add batch metadata
                analysis_result["batch_info"] = {
                    "batch_number": batch_num,
                    "total_batches": total_batches,
                    "professionals_in_batch": len(batch_professionals)
                }
                return analysis_result
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error analyzing batch {batch_num}: {e}")
            return None
    
    def _prepare_analysis_prompt(self, professionals: List[Dict], batch_num: int = 1, total_batches: int = 1) -> str:
        """Prepare the analysis prompt with professional data for a specific batch"""
        
        print(f"📊 Preparing analysis prompt for batch {batch_num}/{total_batches} with {len(professionals)} professionals...")
        
        # Create comprehensive data summary for AI analysis
        data_summary = {
            "batch_info": {
                "batch_number": batch_num,
                "total_batches": total_batches,
                "professionals_in_batch": len(professionals)
            },
            "all_professionals": []
        }
        
        # Add all professionals in this batch to the analysis
        for i, prof in enumerate(professionals):
            professional_data = {
                "id": prof.get('unique_id', f'prof_{i}'),
                "name": f"{prof.get('first_name', '')} {prof.get('last_name', '')}",
                "headline": prof.get('headline', ''),
                "company": prof.get('company', ''),
                "job_title": prof.get('job_title', ''),
                "city": prof.get('city', ''),
                "experience": prof.get('experience', []),
                "connections_count": prof.get('connectionsCount'),
                "follower_count": prof.get('followerCount'),
                "verified": prof.get('verified', False),
                "premium": prof.get('premium', False)
            }
            data_summary["all_professionals"].append(professional_data)
        
        print(f"✅ Prepared {len(data_summary['all_professionals'])} professionals for AI analysis")
        
        # Create the full prompt
        full_prompt = f"""
        {self.credit_scoring_prompt}
        
        BATCH INFORMATION:
        - Batch number: {batch_num} of {total_batches}
        - Professionals in this batch: {len(professionals)}
        
        PROFESSIONAL DATASET (BATCH {batch_num}):
        {json.dumps(data_summary['all_professionals'], indent=2)}
        
        IMPORTANT: Analyze the {len(professionals)} professionals in this batch.
        Calculate accurate years of experience for each professional and provide comprehensive statistical analysis.
        Focus on providing detailed credit scoring insights for this batch.
        This is batch {batch_num} of {total_batches} - analyze only the professionals provided in this batch.
        """
        
        return full_prompt
    
    def _get_gemini_analysis(self, prompt: str) -> Optional[Dict]:
        """Get analysis from Gemini AI with timeout and retry logic"""
        import time
        
        for attempt in range(self.max_retries):
            try:
                print(f"🤖 Sending data to Gemini AI for analysis (attempt {attempt + 1}/{self.max_retries})...")
                
                # Check prompt size and warn if very large
                prompt_size = len(prompt)
                print(f"📊 Prompt size: {prompt_size:,} characters")
                
                if prompt_size > 1000000:  # 1MB
                    print("⚠️  Large dataset detected - this may take longer to process")
                
                # Set generation config with timeout
                generation_config = genai.types.GenerationConfig(
                    temperature=0.1,  # Lower temperature for more consistent results
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8192,  # Maximum output tokens
                )
                
                # Send request with timeout
                start_time = time.time()
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                end_time = time.time()
                
                print(f"✅ Gemini response received in {end_time - start_time:.2f} seconds")
                content = response.text.strip()
                
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    analysis = json.loads(json_str)
                    
                    # Validate the analysis structure
                    if self._validate_analysis(analysis):
                        print("✅ Analysis structure validated successfully")
                        return analysis
                    else:
                        print("⚠️  Analysis structure validation failed")
                        return self._parse_text_analysis(content)
                else:
                    print("⚠️  Could not parse JSON response from Gemini")
                    return self._parse_text_analysis(content)
                    
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error on attempt {attempt + 1}: {error_msg}")
                
                # Check if it's a timeout error
                if "504" in error_msg or "timeout" in error_msg.lower() or "deadline" in error_msg.lower():
                    print(f"⏰ Timeout detected. Retrying in {2 ** attempt} seconds...")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        print("❌ All retry attempts failed due to timeout")
                        return self._handle_large_dataset_fallback(prompt)
                
                # For other errors, don't retry
                print(f"❌ Non-timeout error: {error_msg}")
                return None
        
        return None
    
    def _handle_large_dataset_fallback(self, prompt: str) -> Dict:
        """Handle large datasets that cause timeouts by using manual calculations"""
        print("🔄 Falling back to manual calculations for large dataset...")
        
        try:
            # Extract professional data from the prompt (limited to 50 profiles)
            import re
            json_match = re.search(r'"all_professionals":\s*(\[.*?\])', prompt, re.DOTALL)
            if json_match:
                professionals_json = json_match.group(1)
                professionals = json.loads(professionals_json)
                
                # Calculate metrics manually for the limited dataset
                manual_metrics = self.calculate_experience_metrics(professionals)
                
                return {
                    "analysis_summary": {
                        "total_professionals_analyzed": len(professionals),
                        "professionals_with_experience_data": manual_metrics.get("professionals_with_experience", 0),
                        "average_years_experience": manual_metrics.get("average_years", 0.0),
                        "median_years_experience": manual_metrics.get("median_years", 0.0),
                        "experience_range": {
                            "minimum": manual_metrics.get("min_years", 0.0),
                            "maximum": manual_metrics.get("max_years", 0.0)
                        }
                    },
                    "experience_distribution": {
                        "entry_level_0_2_years": 0,
                        "mid_level_3_7_years": 0,
                        "senior_level_8_15_years": 0,
                        "executive_level_15_plus_years": 0
                    },
                    "career_insights": {
                        "average_job_tenure": manual_metrics.get("average_job_tenure", 0.0),
                        "career_progression_rate": manual_metrics.get("career_progression_rate", 0.0),
                        "industry_stability_score": manual_metrics.get("industry_stability_score", 0.0)
                    },
                    "detailed_analysis": f"Analysis completed using manual calculations due to large dataset timeout. Processed {len(professionals)} professionals (sample from larger database).",
                    "calculation_method": "manual_fallback_timeout",
                    "manual_metrics": manual_metrics,
                    "analysis_scope": f"Sample of {len(professionals)} professionals"
                }
            else:
                return self._create_empty_analysis()
                
        except Exception as e:
            print(f"❌ Error in fallback calculation: {e}")
            return self._create_empty_analysis()
    
    def _validate_analysis(self, analysis: Dict) -> bool:
        """Validate the analysis structure"""
        required_fields = ['analysis_summary', 'experience_distribution', 'career_insights']
        
        for field in required_fields:
            if field not in analysis:
                return False
        
        summary = analysis.get('analysis_summary', {})
        required_summary_fields = ['total_professionals_analyzed', 'average_years_experience']
        
        for field in required_summary_fields:
            if field not in summary:
                return False
        
        return True
    
    def _parse_text_analysis(self, content: str) -> Dict:
        """Parse text analysis when JSON parsing fails"""
        return {
            "analysis_summary": {
                "total_professionals_analyzed": 0,
                "professionals_with_experience_data": 0,
                "average_years_experience": 0.0,
                "median_years_experience": 0.0,
                "experience_range": {"minimum": 0.0, "maximum": 0.0}
            },
            "experience_distribution": {
                "entry_level_0_2_years": 0,
                "mid_level_3_7_years": 0,
                "senior_level_8_15_years": 0,
                "executive_level_15_plus_years": 0
            },
            "career_insights": {
                "average_job_tenure": 0.0,
                "career_progression_rate": 0.0,
                "industry_stability_score": 0.0
            },
            "detailed_analysis": content,
            "parsing_status": "text_only"
        }
    
    def _create_empty_analysis(self) -> Dict:
        """Create empty analysis structure"""
        return {
            "analysis_summary": {
                "total_professionals_analyzed": 0,
                "professionals_with_experience_data": 0,
                "average_years_experience": 0.0,
                "median_years_experience": 0.0,
                "experience_range": {"minimum": 0.0, "maximum": 0.0}
            },
            "experience_distribution": {
                "entry_level_0_2_years": 0,
                "mid_level_3_7_years": 0,
                "senior_level_8_15_years": 0,
                "executive_level_15_plus_years": 0
            },
            "career_insights": {
                "average_job_tenure": 0.0,
                "career_progression_rate": 0.0,
                "industry_stability_score": 0.0
            },
            "detailed_analysis": "No data available for analysis",
            "status": "no_data"
        }
    
    def calculate_experience_metrics(self, professionals: List[Dict]) -> Dict:
        """
        Calculate comprehensive experience and career metrics
        """
        try:
            total_experience = 0
            professionals_with_experience = 0
            experience_years = []
            
            for prof in professionals:
                experience = prof.get('experience', [])
                if experience:
                    # Calculate total years from experience array
                    years = self._calculate_years_from_experience(experience)
                    if years > 0:
                        total_experience += years
                        experience_years.append(years)
                        professionals_with_experience += 1
            
            if professionals_with_experience == 0:
                return {
                    "average_years": 0.0,
                    "total_professionals": len(professionals),
                    "professionals_with_experience": 0,
                    "career_progression_rate": 0.0,
                    "industry_stability_score": 0.0,
                    "average_job_tenure": 0.0
                }
            
            avg_years = total_experience / professionals_with_experience
            experience_years.sort()
            median_years = experience_years[len(experience_years) // 2] if experience_years else 0
            
            # Calculate additional career metrics
            career_progression_rate = self._calculate_career_progression_rate(professionals)
            industry_stability_score = self._calculate_industry_stability_score(professionals)
            average_job_tenure = self._calculate_average_job_tenure(professionals)
            
            return {
                "average_years": round(avg_years, 2),
                "median_years": round(median_years, 2),
                "total_professionals": len(professionals),
                "professionals_with_experience": professionals_with_experience,
                "min_years": min(experience_years) if experience_years else 0,
                "max_years": max(experience_years) if experience_years else 0,
                "career_progression_rate": round(career_progression_rate, 3),
                "industry_stability_score": round(industry_stability_score, 3),
                "average_job_tenure": round(average_job_tenure, 2)
            }
            
        except Exception as e:
            print(f"❌ Error calculating experience metrics: {e}")
            return {"average_years": 0.0, "error": str(e)}
    
    def _calculate_career_progression_rate(self, professionals: List[Dict]) -> float:
        """
        Calculate career progression rate based on job title advancement
        Returns a score between 0 and 1, where higher values indicate better progression
        """
        try:
            progression_indicators = 0
            total_professionals = 0
            
            for prof in professionals:
                experience = prof.get('experience', [])
                if len(experience) >= 2:  # Need at least 2 jobs to assess progression
                    total_professionals += 1
                    
                    # Analyze job titles for progression indicators
                    job_titles = [exp.get('position', '').lower() for exp in experience]
                    
                    # Check for common progression patterns
                    progression_found = False
                    
                    # Pattern 1: Junior -> Senior progression
                    if any('junior' in title for title in job_titles[:-1]) and any('senior' in title for title in job_titles[1:]):
                        progression_found = True
                    
                    # Pattern 2: Assistant -> Manager progression
                    if any('assistant' in title for title in job_titles[:-1]) and any('manager' in title for title in job_titles[1:]):
                        progression_found = True
                    
                    # Pattern 3: Developer -> Lead progression
                    if any('developer' in title for title in job_titles[:-1]) and any('lead' in title for title in job_titles[1:]):
                        progression_found = True
                    
                    # Pattern 4: Analyst -> Director progression
                    if any('analyst' in title for title in job_titles[:-1]) and any('director' in title for title in job_titles[1:]):
                        progression_found = True
                    
                    # Pattern 5: General title advancement (more senior titles)
                    senior_keywords = ['senior', 'lead', 'principal', 'director', 'manager', 'head', 'chief', 'vp', 'c-level']
                    junior_keywords = ['junior', 'assistant', 'associate', 'entry', 'intern']
                    
                    if any(keyword in job_titles[0] for keyword in junior_keywords) and any(keyword in job_titles[-1] for keyword in senior_keywords):
                        progression_found = True
                    
                    if progression_found:
                        progression_indicators += 1
            
            if total_professionals == 0:
                return 0.0
            
            return progression_indicators / total_professionals
            
        except Exception as e:
            print(f"❌ Error calculating career progression rate: {e}")
            return 0.0
    
    def _calculate_industry_stability_score(self, professionals: List[Dict]) -> float:
        """
        Calculate industry stability score based on company consistency and industry focus
        Returns a score between 0 and 1, where higher values indicate more stability
        """
        try:
            stability_indicators = 0
            total_professionals = 0
            
            for prof in professionals:
                experience = prof.get('experience', [])
                if len(experience) >= 1:
                    total_professionals += 1
                    
                    # Get companies and industries
                    companies = [exp.get('companyName', '') for exp in experience]
                    companies = [comp for comp in companies if comp]  # Remove empty values
                    
                    if len(companies) == 0:
                        continue
                    
                    # Indicator 1: Long tenure at companies (stability)
                    avg_tenure = self._calculate_years_from_experience(experience) / len(experience)
                    if avg_tenure >= 2.0:  # Average 2+ years per company
                        stability_indicators += 1
                    
                    # Indicator 2: Same company for multiple positions (internal growth)
                    unique_companies = len(set(companies))
                    if unique_companies < len(companies):  # Some companies appear multiple times
                        stability_indicators += 1
                    
                    # Indicator 3: Fewer company changes (stability)
                    if len(unique_companies) <= 2:  # 2 or fewer companies
                        stability_indicators += 1
                    
                    # Indicator 4: Current position duration (recent stability)
                    if experience:
                        current_duration = self._parse_duration_string(experience[0].get('duration', ''))
                        if current_duration >= 1.5:  # Current position for 1.5+ years
                            stability_indicators += 1
            
            if total_professionals == 0:
                return 0.0
            
            # Normalize to 0-1 scale (max 4 indicators per professional)
            return stability_indicators / (total_professionals * 4)
            
        except Exception as e:
            print(f"❌ Error calculating industry stability score: {e}")
            return 0.0
    
    def _calculate_average_job_tenure(self, professionals: List[Dict]) -> float:
        """
        Calculate average job tenure across all professionals
        """
        try:
            total_tenure = 0
            total_jobs = 0
            
            for prof in professionals:
                experience = prof.get('experience', [])
                if experience:
                    for exp in experience:
                        duration = exp.get('duration', '')
                        if duration:
                            years = self._parse_duration_string(duration)
                            if years > 0:
                                total_tenure += years
                                total_jobs += 1
            
            if total_jobs == 0:
                return 0.0
            
            return total_tenure / total_jobs
            
        except Exception as e:
            print(f"❌ Error calculating average job tenure: {e}")
            return 0.0
    
    def _calculate_years_from_experience(self, experience: List[Dict]) -> float:
        """
        Calculate total years from experience array
        """
        total_years = 0.0
        
        for exp in experience:
            duration = exp.get('duration', '')
            if duration:
                years = self._parse_duration_string(duration)
                total_years += years
        
        return total_years
    
    def _parse_duration_string(self, duration: str) -> float:
        """
        Parse duration string like "2 years 3 months" or "1 year" into years
        """
        try:
            duration = duration.lower().strip()
            years = 0.0
            months = 0.0
            
            # Extract years
            year_match = re.search(r'(\d+)\s*year', duration)
            if year_match:
                years = float(year_match.group(1))
            
            # Extract months
            month_match = re.search(r'(\d+)\s*month', duration)
            if month_match:
                months = float(month_match.group(1))
            
            # Convert months to years
            total_years = years + (months / 12.0)
            return round(total_years, 2)
            
        except Exception:
            return 0.0
    
    def _aggregate_batch_results(self, batch_results: List[Dict], total_professionals: int) -> Dict:
        """Aggregate results from all batches into a comprehensive analysis"""
        try:
            print(f"🔗 Aggregating results from {len(batch_results)} batches...")
            
            # Initialize aggregated metrics
            total_analyzed = 0
            total_with_experience = 0
            all_experience_years = []
            all_career_insights = {
                "average_job_tenure": [],
                "career_progression_rate": [],
                "industry_stability_score": []
            }
            
            # Collect data from all batches
            for batch_result in batch_results:
                summary = batch_result.get('analysis_summary', {})
                insights = batch_result.get('career_insights', {})
                
                total_analyzed += summary.get('total_professionals_analyzed', 0)
                total_with_experience += summary.get('professionals_with_experience_data', 0)
                
                # Collect career insights for averaging
                if insights.get('average_job_tenure', 0) > 0:
                    all_career_insights['average_job_tenure'].append(insights['average_job_tenure'])
                if insights.get('career_progression_rate', 0) > 0:
                    all_career_insights['career_progression_rate'].append(insights['career_progression_rate'])
                if insights.get('industry_stability_score', 0) > 0:
                    all_career_insights['industry_stability_score'].append(insights['industry_stability_score'])
            
            # Calculate aggregated metrics
            avg_job_tenure = sum(all_career_insights['average_job_tenure']) / len(all_career_insights['average_job_tenure']) if all_career_insights['average_job_tenure'] else 0.0
            avg_progression_rate = sum(all_career_insights['career_progression_rate']) / len(all_career_insights['career_progression_rate']) if all_career_insights['career_progression_rate'] else 0.0
            avg_stability_score = sum(all_career_insights['industry_stability_score']) / len(all_career_insights['industry_stability_score']) if all_career_insights['industry_stability_score'] else 0.0
            
            # Create aggregated result
            aggregated_result = {
                "analysis_summary": {
                    "total_professionals_analyzed": total_analyzed,
                    "professionals_with_experience_data": total_with_experience,
                    "total_batches_processed": len(batch_results),
                    "analysis_scope": f"Complete database analysis ({total_professionals} professionals in {len(batch_results)} batches)"
                },
                "experience_distribution": {
                    "entry_level_0_2_years": 0,
                    "mid_level_3_7_years": 0,
                    "senior_level_8_15_years": 0,
                    "executive_level_15_plus_years": 0
                },
                "career_insights": {
                    "average_job_tenure": round(avg_job_tenure, 2),
                    "career_progression_rate": round(avg_progression_rate, 3),
                    "industry_stability_score": round(avg_stability_score, 3)
                },
                "detailed_analysis": f"Comprehensive analysis completed across {len(batch_results)} batches. Total professionals analyzed: {total_analyzed}.",
                "calculation_method": "batched_ai_analysis",
                "batch_details": [
                    {
                        "batch_number": result.get("batch_info", {}).get("batch_number", 0),
                        "professionals_analyzed": result.get("batch_info", {}).get("professionals_in_batch", 0)
                    }
                    for result in batch_results
                ]
            }
            
            print(f"✅ Aggregated results from {len(batch_results)} batches successfully")
            return aggregated_result
            
        except Exception as e:
            print(f"❌ Error aggregating batch results: {e}")
            return self._create_empty_analysis()
    
    def close(self):
        """Close database connection"""
        if self.db_manager:
            self.db_manager.close()


def main():
    """Test the professional credit scorer"""
    try:
        print("🚀 Starting Professional Credit Scorer Test")
        print("=" * 50)
        
        # Initialize the credit scorer
        scorer = ProfessionalCreditScorer()
        
        # Analyze the professional database
        analysis = scorer.analyze_professional_database()
        
        # Display results
        print("\n📊 CREDIT SCORING ANALYSIS RESULTS")
        print("=" * 50)
        
        if analysis:
            summary = analysis.get('analysis_summary', {})
            print(f"Total professionals analyzed: {summary.get('total_professionals_analyzed', 0)}")
            print(f"Professionals with experience data: {summary.get('professionals_with_experience_data', 0)}")
            print(f"Average years of experience: {summary.get('average_years_experience', 0.0)}")
            print(f"Median years of experience: {summary.get('median_years_experience', 0.0)}")
            
            experience_range = summary.get('experience_range', {})
            print(f"Experience range: {experience_range.get('minimum', 0.0)} - {experience_range.get('maximum', 0.0)} years")
            
            print("\n📈 EXPERIENCE DISTRIBUTION")
            distribution = analysis.get('experience_distribution', {})
            for level, count in distribution.items():
                print(f"  {level}: {count}")
            
            print("\n💼 CAREER INSIGHTS")
            insights = analysis.get('career_insights', {})
            for insight, value in insights.items():
                print(f"  {insight}: {value}")
            
            print("\n📝 DETAILED ANALYSIS")
            detailed = analysis.get('detailed_analysis', 'No detailed analysis available')
            if len(detailed) > 500:
                print(detailed[:500] + "...")
            else:
                print(detailed)
        
        # Close connections
        scorer.close()
        
        print("\n✅ Professional Credit Scorer completed")
        
    except Exception as e:
        print(f"❌ Error in main test: {e}")


if __name__ == "__main__":
    main() 