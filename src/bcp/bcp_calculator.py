"""
BCP Calculator

This module orchestrates the flow for calculating Business Complexity Points (BCP)
of user stories using a series of predefined prompts and GPT-4o.
"""

import json
import logging
import math
import os
from typing import Dict, Any, List

from .prompt_handler import PromptHandler
from .logger import StepLogger

class BCPCalculator:
    """
    Calculator for Business Complexity Points (BCP) of user stories.
    """
    
    def __init__(self, logger: logging.Logger, provider_name: str = "openai"):
        """
        Initialize the BCP calculator.
        
        Args:
            logger: The logger instance
            provider_name: The name of the LLM provider to use ('openai' or 'claude')
        """
        self.logger = logger
        self.provider_name = provider_name
        self.prompt_handler = PromptHandler(logger, provider_name=provider_name)
        
        # Define the steps in the BCP calculation process
        self.steps = [
            {
                "name": "Story Maturity Complexity",
                "prompt_file": "step1_flow_story_maturity_complexity.jinja2",
                "required": False  # Not used for BCP calculation, but for additional analysis
            },
            {
                "name": "Story INVEST Maturity",
                "prompt_file": "step2_flow_story_invest_maturity.jinja2",
                "required": False  # Not used for BCP calculation, but for additional analysis
            },
            {
                "name": "Break Elements",
                "prompt_file": "step3_flow_bcp_break_elements.jinja2",
                "required": True  # Required for BCP calculation
            },
            {
                "name": "External Integrations Complexity",
                "prompt_file": "step4_flow_bcp_boundaries.jinja2",
                "required": True  # Required for BCP calculation
            },
            {
                "name": "UI Elements Complexity",
                "prompt_file": "step5_flow_bcp_interface_elements.jinja2",
                "required": True  # Required for BCP calculation
            },
            {
                "name": "Business Rules Complexity",
                "prompt_file": "step6_flow_bcp_business_rule.jinja2",
                "required": True  # Required for BCP calculation
            }
        ]
    
    def calculate_bcp(self, story_content: str) -> Dict[str, Any]:
        """
        Calculate the Business Complexity Points (BCP) for a user story.
        
        Args:
            story_content: The content of the user story
            
        Returns:
            A dictionary containing the results of each step and the final BCP
        """
        self.logger.info("Starting BCP calculation")
        
        # Extract story name from content (assuming first line is the title)
        story_lines = story_content.strip().split('\n')
        story_name = story_lines[0] if story_lines else "Unnamed Story"
        
        # Initialize results dictionary
        results = {
            "story_name": story_name,
            "steps": {},
            "breakdown": {},
            "total_bcp": 0
        }
        
        # Process each step
        elements = None
        
        for step in self.steps:
            step_name = step["name"]
            step_logger = StepLogger(self.logger, step_name)
            step_logger.info(f"Processing step: {step_name}")
            
            try:
                # Prepare variables for the prompt
                variables = {"story": story_content, "storyName": story_name}
                response = {}
                
                # For steps 4-6, we need the output from step 3
                if step["name"] == "External Integrations Complexity" and elements:
                    # Extract all instances from elements['Integrations (Boundaries)'] and set as comma-separated string
                    variables["elements"] = ""
                    if isinstance(elements, dict) and "Integrations (Boundaries)" in elements:
                        boundaries = elements["Integrations (Boundaries)"]
                        if isinstance(boundaries, list):
                            variables["elements"] = ", ".join(str(b) for b in boundaries)
                        else:
                            variables["elements"] = str(boundaries)
                    step_logger.debug(f"Using boundaries section: {variables['elements']}")
                    # If no elements found, set default response
                    if not variables["elements"]:
                        response = [{
                            "Boundary": 1,
                            "Summary": "There is no external integration detected",
                            "Size": "XS"
                        }]
                
                elif step["name"] == "UI Elements Complexity" and elements:
                    # Extract interface elements section from elements
                    variables["elements"] = ""
                    if isinstance(elements, dict):
                        interface_elements = {}                        
                        if "User View" in elements:
                            interface_elements['User View'] = elements.get('User View')
                        if "Acceptance Criteria" in elements:
                            interface_elements['Acceptance Criteria'] = ", ".join(str(b) for b in elements["Acceptance Criteria"])
                        if "Test Plan" in elements:
                            interface_elements['Test Plan'] = elements.get('Test Plan')
                        variables["elements"] = json.dumps(interface_elements, ensure_ascii=False, indent=2).replace("'", "").replace('"', "")
                    step_logger.debug(f"Using interface section: {variables['elements']}")
                    # If no elements found, set default response
                    if not variables["elements"]:
                        response = {
                            "step": "Interface",
                            "description": "There is no interface elements detected",
                            "total": 0
                        }
                
                elif step["name"] == "Business Rules Complexity" and elements:
                    # Extract business rules section from elements
                    variables["elements"] = ""
                    if isinstance(elements, dict):
                        business_elements = {}                        
                        if "Business Narrative" in elements:
                            business_elements['Business Narrative'] = elements.get('Business Narrative')
                        if "Requirements and Business Rules" in elements:
                            business_elements['Requirements and Business Rules'] = elements.get('Requirements and Business Rules')
                        if "Test Plan" in elements:
                            business_elements['Test Plan'] = elements.get('Test Plan')
                        variables["elements"] = json.dumps(business_elements, ensure_ascii=False, indent=2).replace("'", "").replace('"', "")
                    step_logger.debug(f"Using business section: {variables['elements']}")
                    # If no elements found, set default response
                    if not variables["elements"]:
                        response = {
                            "step": "Business",
                            "description": "There is no logical rules detected",
                            "total": 0
                        }

                # Process the prompt, if response is not set
                if not response:
                    response = self.prompt_handler.process_prompt(step["prompt_file"], variables)
                step_logger.info(f"Step completed successfully")
                
                # Store the result
                results["steps"][step_name] = response
                
                # If this is step 3, store the elements for later steps
                if step["name"] == "Break Elements":
                    #elements = response.get("raw_response", "")
                    elements = response
                
                # If this is a required step (4-6), add to BCP calculation
                if step["required"] and step["name"] != "Break Elements":
                    step_logger.debug(f"Response:\n {json.dumps(response, ensure_ascii=False)}")
                    total_bcp = 0
                    
                    # Check if response is a string, which indicates parsing error
                    if isinstance(response, str):
                        step_logger.warning(f"Response is a string, not a parsed object: {response}")
                        response = {"raw_response": response}
                    
                    if isinstance(response, dict) and "raw_response" in response:
                        step_logger.warning("Using raw_response as fallback")
                        # Skip BCP calculation for this step
                        continue
                        
                    match step["name"]:
                        case "External Integrations Complexity":
                            # Make sure response is a list
                            if not isinstance(response, list):
                                step_logger.warning(f"Expected list for boundaries but got {type(response)}")
                                continue
                                
                            for boundary in response:
                                if isinstance(boundary, dict):
                                    boundary_size = boundary.get("Size", "")
                                    match boundary_size:
                                        case "XS":
                                            total_bcp += 1
                                        case "S":
                                            total_bcp += 2
                                        case "M":
                                            total_bcp += 3
                                        case "XL":
                                            total_bcp += 8
                        case "UI Elements Complexity":
                            # Make sure response is a dict
                            if not isinstance(response, dict):
                                step_logger.warning(f"Expected dict for UI Elements but got {type(response)}")
                                continue
                                
                            total_bcp += math.ceil(response.get("Static", 0) / 5) * 3
                            total_bcp += math.ceil(response.get("Dynamic", 0) / 5) * 5
                        case "Business Rules Complexity":
                            # Make sure response is a list
                            if not isinstance(response, list):
                                step_logger.warning(f"Expected list for Business Rules but got {type(response)}")
                                continue
                                
                            for rule in response:
                                if isinstance(rule, dict):
                                    total_bcp += rule.get("Score", 0)

                    if total_bcp > 0:
                        component_name = step["name"].replace(" Complexity", "")
                        results["breakdown"][component_name] = total_bcp
                        results["total_bcp"] += total_bcp
                    else:
                        step_logger.warning(f"No BCP value found in response: {response}")

            except Exception as e:
                step_logger.error(f"Error processing step: {str(e)}")
                results["steps"][step_name] = {"error": str(e)}
                
                # If this is a required step and it failed, we can't calculate the BCP
                if step["required"]:
                    self.logger.error("Required step failed, cannot calculate BCP")
                    results["error"] = f"Failed to calculate BCP: {str(e)}"
                    return results
        
        self.logger.info(f"BCP calculation completed. Total BCP: {results['total_bcp']}")
        return results
    
    def _extract_section(self, elements_text: str, section_number: int) -> str:
        """
        Extract a specific section from the elements text.
        
        Args:
            elements_text: The text containing all elements
            section_number: The section number to extract (1=Business Rules, 2=Interface, 3=External)
            
        Returns:
            The extracted section text
        """
        sections = elements_text.split("<-->")
        
        if len(sections) >= section_number:
            return sections[section_number - 1].strip()
        else:
            self.logger.warning(f"Section {section_number} not found in elements text")
            return ""