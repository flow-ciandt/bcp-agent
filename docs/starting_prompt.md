I need to create a new project, this will be a gen ai project. Wht it needs to do is to help me calculate the Business complexity points (BCP for shorts) of an user story. The method to count the BCP is already implemented in a 6 prompts (steps1 to step6), this steps are already in the "prompts" folder. 

 - Steps 1 and 2 are validations of complexity and invest maturity, they are complementar analysis.
 - Step3 breakts the story into 3 elements Bounderies, Interface and business rules
 - step4 gets the boundary elements and calculate the complexituy
 - Step5 gets the user interface elements and calculate the complexity
 - step6 gets the business rules elements and calculate the complexity.


What I need from you is to help me create a command line interface application that will receive a user story (md file) and will structure the call between all the 6 steps. aditional requirements:

Acceptance Criteria:
 - The application should run as CLI 
 - The applicatiou should orchestrate the flow, get the complexity points from steps 4 to 6, and sum it by the end
 - The final outcome should be The output of each step executed, and the overall business complexity point given by the above rule.

Initial tech requirements:
 - Implement the application in python
 - Implement the orchestration of this flow using langchain
 - Use OpenAI as the provider for the models and the GPT-4o as the model to be leveraged
 - Create proper logging so we can understand the steps and decisions of the application

