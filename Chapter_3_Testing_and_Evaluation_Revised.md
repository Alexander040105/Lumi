# 9.8. Testing and Evaluation

This section outlines the comprehensive testing and evaluation procedures employed to validate the correctness, usability, and overall quality of the LUMI platform. The testing process is structured into four phases: unit testing, usability testing, system testing, and a pilot run. Each phase serves a distinct purpose in ensuring that the system functions as intended and meets the needs of its target users.

## 9.8.1. Unit Testing

Unit testing was performed during the development phase to verify the correctness of individual components and modules of the system. This includes testing specific functions such as user authentication, renewable energy calculations, forecast data retrieval, Ecosim simulation triggers, and AI assistant query handling. The goal is to detect and resolve errors early before deploying the system as a whole.

For the renewable energy calculation modules, unit tests were written to validate the solar temperature factor, performance ratio aggregation, wind power output, runoff coefficient estimation, micro-hydropower design flow, and economic viability scoring. Each test supplies synthetic climate and terrain inputs representing Philippine municipal conditions and asserts that the returned values fall within physically plausible ranges. Machine learning preprocessing functions were tested using fixture-based parameterized inputs to ensure that missing value imputation, feature engineering, and train-test splitting behaved correctly across edge cases.

Frontend components were tested using the React Testing Library with Vitest to verify that dashboard charts render correctly, form validations trigger appropriately, and navigation flows behave as expected. Backend API endpoints were tested using pytest with HTTPX to confirm that authentication, forecast retrieval, Ecosim submission, and AI assistant interactions return the correct status codes and response structures.

## 9.8.2. Usability Testing

A sample size of 196 respondents participated in usability testing, either on-site or remotely, depending on their convenience. The sample size was determined using Cochran's formula based on the CALABARZON population and a 7% margin of error. A 7% margin of error is appropriate for this study, as it provides a balance between precision and feasibility, ensuring that the results are representative of the population while keeping the sample size manageable.

During testing, participants were assigned structured tasks involving key platform features such as account creation, EnergyHub dashboard navigation, forecast exploration, Ecosim simulation execution, map interpretation, and AI assistant interaction. To ensure meaningful engagement, the following validation strategies were implemented:

The system included task-based activity logs that track user actions, time spent on each module, number of simulation attempts, and completion timestamps. Participants answered follow-up validation questions and submitted a brief short-answer reflection summarizing what they learned and the decisions they made during each simulation. The System Usability Scale (SUS) and a custom Likert-scale questionnaire were administered after testing to quantify interface clarity, navigation efficiency, and overall satisfaction.

## 9.8.3. System Testing

System testing involved checking the entire platform as a whole to ensure that all modules work together as intended. This includes validating integrations between the React frontend interface, FastAPI backend services, machine learning prediction pipeline, and Supabase PostgreSQL database. It also covered performance under various conditions, such as concurrent user load and diverse input variety.

End-to-end scenarios were executed to verify complete user workflows: from registration and login, through EnergyHub dashboard loading and forecast visualization, to Ecosim simulation submission and result interpretation. Integration tests confirmed that frontend requests to backend endpoints returned valid JSON within acceptable response times, that database queries resolved foreign key relationships correctly, and that the ML predictor loaded pre-computed forecast artifacts without errors.

Performance testing was conducted to evaluate the system's behavior under stress. Scenarios included rendering historical trend charts with twenty years of multi-series data, submitting concurrent Ecosim requests for multiple municipalities, and measuring API response times under simulated load. The system was also observed for memory stability during continuous operation to ensure no monotonic growth or leaks occurred in the backend service.

## 9.8.4. Pilot Run

The pilot run was conducted prior to formal evaluation to gather direct feedback and open-ended suggestions from actual users. This early phase focused on collecting insights that would guide improvements to both the platform's design and recommendation content before any major testing or implementation. The goal was to ensure that the development remained aligned with user expectations and needs.

Participants included household decision-makers from CALABARZON, barangay officials from selected reference provinces, licensed electrical and electronics engineers, and students from Information Technology, Computer Science, and Engineering programs. They were asked to freely explore the LUMI platform, interact with its EnergyHub dashboard, execute Ecosim simulations for their home municipalities, and converse with the AI assistant. They then provided detailed feedback on areas such as clarity of visualizations, navigation intuitiveness, recommendation usefulness, and overall experience.

By placing emphasis on user suggestions and improvement-oriented feedback, the pilot run served as a foundation for refining the platform prior to structured evaluation phases such as usability assessments, ISO 25010 questionnaire administration, and expert validation interviews. Observations from the pilot deployment were recorded to identify final areas for refinement before the system was considered ready for broader use.
