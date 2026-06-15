# CHAPTER 3

# METHODOLOGY

This chapter presents the research design, development methodology, requirements specifications, data gathering procedures, and system development procedures employed in the construction of LUMI: Data-Driven Environmental Intelligence System for Renewable Energy Decision Support. The chapter outlines the iterative and incremental approach to software development, the functional and non-functional requirements that guided system design, the tools and technologies utilized throughout the project, and the procedures followed to ensure the reliability and validity of the system's outputs.

---

## 3.1 Research Design

This study employs a developmental research design focused on the creation, implementation, and evaluation of a web-based environmental intelligence system. Developmental research is appropriate for this study as it involves the systematic design, development, and assessment of a software system that addresses a specific practical problem, in this case, the need for accessible, data-driven insights for renewable energy decision-making in the Philippines.

The research integrates quantitative and qualitative evaluation methods. Quantitative methods are applied in the assessment of machine learning model performance through statistical metrics such as Mean Absolute Error (MAE), Root Mean Square Error (RMSE), and R-squared values. Additionally, computational performance metrics including response time, memory utilization, and CPU utilization are measured to evaluate system efficiency. Qualitative methods are employed in the evaluation of the AI assistant's responses, where expert judgment and relevance assessment are necessary due to the generative nature of large language model outputs. This mixed-methods approach ensures that both the technical performance and the practical utility of the system are rigorously evaluated.

---

## 3.2 Participants or Respondents

[To be determined based on the evaluation phase. The study will identify potential users, energy practitioners, and academic experts who will participate in user acceptance testing and expert validation of the system's recommendations and predictions. Details regarding the number of participants, selection criteria, and demographic information will be inserted here upon completion of respondent recruitment.]

---

## 3.3 Project Development Methodology (Software Development Life Cycle)

### 3.3.1 Definition of the Iterative and Incremental Development Approach

The development of LUMI follows an Iterative and Incremental Software Development Life Cycle (SDLC) model. In this approach, the system is developed through repeated cycles or iterations, where each iteration encompasses a complete sequence of planning, analysis, design, implementation, testing, and evaluation activities. At the conclusion of each iteration, a functional increment of the system is produced, building upon the capabilities established in previous cycles. This methodology allows for progressive refinement of system features, incorporation of feedback at regular intervals, and adaptation to evolving requirements throughout the development process.

Unlike traditional linear models such as the Waterfall approach, where each phase must be fully completed before the next begins, the iterative and incremental model permits overlapping and revisiting of phases. Early iterations focus on core functionalities and proof-of-concept implementations, while subsequent iterations expand the system's capabilities, improve performance, and enhance user experience based on insights gained from testing and stakeholder feedback.

### 3.3.2 Suitability of the Iterative and Incremental Approach for LUMI

The iterative and incremental development model was selected for LUMI due to the complex and multifaceted nature of the system. LUMI integrates multiple specialized components including machine learning prediction modules, statistical time-series forecasting, environmental data processing pipelines, AI-assisted decision support, and interactive data visualizations. The interdependencies among these components necessitate an approach where foundational modules can be developed, tested, and validated independently before full system integration.

Furthermore, the system's reliance on external data sources, APIs, and evolving machine learning methodologies requires flexibility in development. The iterative approach accommodates adjustments to data schemas, model architectures, and API integrations without necessitating a complete redesign of the system. It also supports the experimental nature of machine learning development, where model selection, hyperparameter tuning, and feature engineering are inherently iterative processes that benefit from continuous evaluation and refinement.

The incremental nature of the model ensures that stakeholders and potential users can interact with functional components of the system at early stages, providing feedback that informs subsequent development. This is particularly valuable for the user interface and AI assistant components, where usability and response quality are best assessed through hands-on evaluation.

### 3.3.3 Phases of the Iterative and Incremental Development

The following phases describe the structured activities conducted within each iteration of the development cycle. The exact timeline and scheduling of these phases are subject to finalization based on project milestones and academic requirements.

#### Phase 1: Planning

**Purpose.** The planning phase establishes the foundation for each development iteration by defining objectives, identifying resources, and establishing the scope of work to be completed within the iteration. It ensures that development activities are aligned with the overall goals of the project and that potential risks are identified and mitigated early.

**Activities.** Define iteration objectives and deliverables based on the overall project roadmap and feedback from previous iterations; identify required datasets, APIs, and external resources needed for the iteration; allocate development tasks among team members and establish accountability; assess technical risks, dependencies, and constraints that may affect the iteration; prepare development environments and ensure access to necessary tools and platforms.

**Expected Outputs.** Iteration plan document outlining objectives, scope, and task assignments; risk assessment and mitigation plan; updated project timeline and milestone tracker; resource allocation sheet.

#### Phase 2: Requirements Analysis

**Purpose.** The requirements analysis phase captures and formalizes the functional and non-functional requirements that the system increment must satisfy. It bridges the gap between user needs and technical implementation by producing detailed specifications that guide design and development activities.

**Activities.** Gather and review user requirements, stakeholder feedback, and system constraints; analyze existing system capabilities and identify gaps to be addressed in the current iteration; document functional requirements using formal "shall" statements; define acceptance criteria for each requirement; validate requirements with stakeholders and refine based on feedback.

**Expected Outputs.** Requirements specification document for the current iteration; use case diagrams and user stories where applicable; acceptance criteria checklist; requirements traceability matrix.

#### Phase 3: System Design

**Purpose.** The system design phase translates requirements into architectural and detailed design specifications. It defines the structure of the system, the interactions among components, database schemas, user interface layouts, and the algorithms that will be implemented.

**Activities.** Design or update system architecture diagrams showing component interactions; create or refine database schemas, entity-relationship diagrams, and data flow diagrams; design user interface mockups and prototype layouts for new features; specify algorithms, machine learning model architectures, and data processing pipelines; define API contracts and integration points between frontend, backend, and external services.

**Expected Outputs.** System architecture documentation; database design documents and schema definitions; UI/UX design mockups and wireframes; API specification documents; algorithm design templates and pseudocode.

#### Phase 4: Development / Implementation

**Purpose.** The development phase involves the actual coding and construction of the system increment according to the specifications established in the design phase. It encompasses frontend development, backend API implementation, machine learning model training, data pipeline construction, and integration with external services.

**Activities.** Implement frontend components and user interface features using the selected frontend framework; develop backend APIs, business logic, and data access layers; implement or refine machine learning models and statistical forecasting modules; build and optimize data ingestion and preprocessing pipelines; integrate external APIs including Google Gemini and Groq for AI-assisted decision support; conduct unit testing during development to identify and resolve defects early.

**Expected Outputs.** Source code for all implemented features and components; unit test results and code coverage reports; trained machine learning models and serialized model artifacts; API documentation and endpoint definitions; data pipeline configuration files.

#### Phase 5: Testing

**Purpose.** The testing phase validates that the developed increment meets the specified requirements and functions correctly within the integrated system. It encompasses multiple levels of testing to identify defects, verify functionality, and ensure that new changes do not adversely affect existing capabilities.

**Activities.** Execute unit tests to verify individual components and functions; perform integration testing to validate interactions among frontend, backend, database, and external services; conduct functional testing against requirements to verify correct behavior; evaluate machine learning models using statistical performance metrics; test API endpoints for correctness, response time, and error handling; perform user interface testing for usability, responsiveness, and cross-browser compatibility; document defects and track resolution.

**Expected Outputs.** Test plan and test case documentation; test execution reports with pass/fail status; machine learning model evaluation results; API testing reports; defect log and resolution tracking sheet.

#### Phase 6: Evaluation

**Purpose.** The evaluation phase assesses the overall quality, performance, and usability of the system increment. It goes beyond defect detection to measure how well the system achieves its intended objectives and identifies opportunities for improvement in subsequent iterations.

**Activities.** Evaluate machine learning prediction accuracy using held-out test datasets and appropriate statistical metrics; measure computational performance including response time, memory utilization, and CPU utilization under various load conditions; assess AI assistant response quality through benchmark questions and expert validation; gather user feedback through usability testing sessions and structured questionnaires; review system outputs including visualizations, reports, and recommendations for correctness and clarity; analyze evaluation results and identify priorities for the next iteration.

**Expected Outputs.** Model performance evaluation report; computational performance benchmark results; AI assistant evaluation report; user feedback summary and usability assessment; iteration retrospective and improvement recommendations.

#### Phase 7: Deployment

**Purpose.** The deployment phase makes the validated system increment available for use in the target environment. It involves configuring the production or staging environment, deploying application code, setting up databases, and ensuring that the system is accessible to intended users.

**Activities.** Prepare deployment environment and configure hosting infrastructure; deploy backend services, frontend application, and database schemas; configure environment variables, API keys, and security settings; verify deployed system functionality through smoke testing; monitor system logs and performance metrics post-deployment; document deployment procedures and rollback plans.

**Expected Outputs.** Deployed and accessible system instance; deployment documentation and configuration records; smoke test results confirming operational status; monitoring dashboard and alert configurations; maintenance and support plan.

---

## 3.4 Requirements Specifications: Tools, Technologies, or Platforms Used

### 3.4.1 Functional Requirements

The following functional requirements specify the capabilities that LUMI shall provide to its users and stakeholders. These requirements are expressed in formal "shall" statements to ensure clarity and testability.

**User Interaction.** The system shall provide a user-friendly web interface that allows users to navigate between modules including the climate and energy dashboard, forecasting tools, recommendation engine, and AI assistant. The system shall support user authentication and session management to ensure secure access to personalized features and saved preferences. The system shall allow users to select Philippine regions and localities to receive localized energy and environmental insights.

**Renewable Energy Forecasting.** The system shall implement machine learning models capable of forecasting renewable energy potential for solar, wind, and hydroelectric sources based on historical and environmental data. The system shall display forecasted renewable energy output with appropriate confidence intervals and temporal granularity.

**Energy Demand Forecasting.** The system shall implement statistical time-series forecasting models to predict future energy demand trends based on historical consumption patterns. The system shall present energy demand forecasts through interactive visualizations that allow users to explore projections across different time horizons.

**Data Ingestion.** The system shall ingest publicly available energy datasets from the Department of Energy (DOE) and environmental datasets from relevant Philippine government agencies. The system shall support automated data retrieval from external APIs and manual import of structured datasets in standard formats such as CSV and JSON.

**Data Preprocessing.** The system shall implement data preprocessing pipelines that handle missing values, outlier detection, data normalization, and feature engineering prior to model training. The system shall validate incoming data for format consistency, completeness, and integrity before processing.

**Machine Learning Prediction Modules.** The system shall implement supervised learning algorithms for regression tasks related to energy output and demand prediction. The system shall provide functionality for model training, hyperparameter tuning, cross-validation, and performance evaluation. The system shall store trained model artifacts and metadata in a versioned manner to support reproducibility and comparison.

**Statistical Forecasting Modules.** The system shall implement statistical forecasting techniques such as AutoRegressive Integrated Moving Average (ARIMA) and related time-series methods for baseline comparison and trend analysis. The system shall generate forecast outputs with diagnostic plots including residual analysis and autocorrelation functions.

**AI Assistant Integration.** The system shall integrate an AI assistant capable of interpreting user queries related to renewable energy, climate data, and energy demand. The system shall process natural language inputs and generate informative, contextually relevant responses based on system data and retrieved knowledge.

**Gemini and Groq API Interaction.** The system shall interface with the Google Gemini API and Groq API to leverage large language model capabilities for decision support and recommendation generation. The system shall implement prompt engineering strategies to ensure that API inputs are structured for optimal response quality and relevance. The system shall handle API errors, rate limits, and fallback mechanisms to maintain service availability.

**Visualization and Dashboard.** The system shall provide interactive data visualizations including charts, graphs, and maps to represent climate patterns, energy trends, and forecast results. The system shall implement a responsive dashboard layout that adapts to various screen sizes and devices.

**Reports and Recommendations.** The system shall generate structured reports summarizing energy forecasts, renewable energy potential assessments, and recommendation rationales. The system shall present recommendation outputs in a clear, actionable format suitable for non-technical users.

**Model Results Display.** The system shall display model performance metrics, prediction results, and comparative analyses in an interpretable format. The system shall provide model explanation features that highlight key factors influencing predictions.

**Data Storage.** The system shall persistently store energy datasets, environmental data, model outputs, user interactions, and AI assistant responses in a structured database. The system shall implement data access controls to ensure the security and privacy of stored information.

**Deployment Access.** The system shall be deployable as a web application accessible through standard internet browsers without requiring specialized client software. The system shall provide consistent performance and availability within the constraints of the chosen deployment platform.

---

### 3.4.2 Software Requirements

The following table summarizes the tools, technologies, and platforms utilized in the development and operation of LUMI.

| Category | Tool / Technology | Purpose | Usage in LUMI |
|----------|-------------------|---------|---------------|
| Development Environment | Visual Studio Code | Integrated development environment for writing, debugging, and managing code across the entire project. | Primary IDE for frontend, backend, and scripting development. |
| Programming Languages | Python 3.12+ | Backend development, machine learning model implementation, data processing, and API services. | Used for FastAPI backend, ML pipelines, data extraction, and forecasting notebooks. |
| Programming Languages | JavaScript (ES6+) | Frontend application logic, component interactivity, and client-side data handling. | Used for React-based user interface development. |
| Programming Languages | HTML5 / CSS3 | Web page structure and styling for the frontend application. | Used within the React framework for UI rendering and Tailwind CSS styling. |
| Machine Learning Libraries | scikit-learn | General-purpose machine learning algorithms including regression, classification, and preprocessing utilities. | Used for feature engineering, model training, and baseline prediction tasks. |
| Machine Learning Libraries | statsmodels | Statistical modeling and time-series analysis including ARIMA implementation. | Used for energy demand forecasting and diagnostic statistical tests. |
| Machine Learning Libraries | PyTorch | Deep learning framework for building and training neural network models. | Used for advanced forecasting models and experimental deep learning components. |
| Machine Learning Libraries | pandas | Data manipulation, cleaning, transformation, and analysis. | Used throughout data pipelines, ETL processes, and exploratory data analysis. |
| Machine Learning Libraries | NumPy | Numerical computing, array operations, and mathematical computations. | Used for matrix operations, statistical calculations, and model input preparation. |
| Data Processing Tools | Jupyter Notebook | Interactive development environment for data exploration, prototyping, and documentation of analysis workflows. | Used in DOE_Data_Extracted for ARIMA forecasting experiments and data cleaning. |
| Data Processing Tools | rasterio / geopandas | Geospatial data processing and raster analysis. | Used in the terrain pipeline for elevation data processing and geographic feature extraction. |
| Database | PostgreSQL (via Supabase) | Relational database management for structured data storage and retrieval. | Used for storing energy datasets, environmental data, model outputs, and user interactions. |
| Database | Redis | In-memory data store for caching, session management, and high-speed data access. | Used for caching frequently accessed data and managing temporary computation results. |
| Backend Framework | FastAPI | Modern, high-performance web framework for building RESTful APIs with Python. | Used as the primary backend framework for API endpoints, authentication, and business logic. |
| Backend Framework | Uvicorn | ASGI server implementation for serving FastAPI applications. | Used as the HTTP server for the backend application. |
| Frontend Framework | React 18+ | Component-based JavaScript library for building interactive user interfaces. | Used for constructing the dashboard, visualization components, and AI assistant interface. |
| Frontend Framework | Vite | Frontend build tool and development server. | Used for bundling, hot-module replacement, and production builds of the React application. |
| Frontend Framework | Tailwind CSS | Utility-first CSS framework for rapid and consistent UI styling. | Used for styling all frontend components with responsive design. |
| Visualization Tools | Recharts / D3.js | Data visualization libraries for rendering interactive charts and graphs. | Used for displaying energy trends, forecast results, and climate pattern visualizations. |
| Visualization Tools | Leaflet / React-Leaflet | Interactive mapping library for geospatial data visualization. | Used for the region selection module and geographic energy data display. |
| AI APIs | Google Gemini API | Large language model API for natural language understanding and generation. | Used for AI assistant responses, recommendation explanations, and decision support content. |
| AI APIs | Groq API | High-performance inference API for large language models. | Used as an alternative or complementary LLM inference provider for AI assistant features. |
| AI APIs | sentence-transformers | Sentence and text embedding library for semantic similarity and retrieval. | Used for embedding generation in RAG-based knowledge retrieval pipelines. |
| AI APIs | FAISS | Vector similarity search library for efficient nearest-neighbor retrieval. | Used for storing and querying text embeddings in the AI knowledge retrieval system. |
| Deployment Platform | Netlify / Vercel (Frontend) | Cloud platform for static site deployment and CDN distribution. | Used for hosting the built React frontend application. |
| Deployment Platform | Render / Railway / AWS (Backend) | Cloud platform for deploying and scaling backend services. | Used for hosting the FastAPI backend, running background workers, and serving APIs. |
| Version Control | Git | Distributed version control system for tracking code changes and collaboration. | Used for managing source code history, branching, and team collaboration via GitHub. |

---

### 3.4.3 Hardware Requirements

The following table outlines the hardware requirements for developing and operating LUMI. The development requirements reflect the specifications of the machines used by the researchers during the construction of the system, while the minimum and recommended requirements represent the expected client-side and server-side configurations for running the deployed application.

| Category | Minimum Requirement | Recommended Requirement | Development Requirement |
|----------|---------------------|------------------------|------------------------|
| Processor | Intel Core i3 or AMD Ryzen 3 (quad-core, 2.0 GHz) | Intel Core i5 or AMD Ryzen 5 (hexa-core, 2.5 GHz) | Intel Core i7 or AMD Ryzen 7 (octa-core, 2.8 GHz) |
| RAM | 8 GB DDR4 | 16 GB DDR4 | 32 GB DDR4 |
| Storage | 256 GB SSD | 512 GB SSD | 1 TB SSD |
| GPU | Integrated graphics (sufficient for web rendering) | Dedicated GPU with 4 GB VRAM (for accelerated ML training) | NVIDIA GPU with CUDA support, 8 GB+ VRAM (for deep learning experimentation) |
| Internet Connection | Stable broadband connection (5 Mbps) | High-speed broadband connection (25 Mbps) | High-speed broadband connection (50 Mbps or higher) |
| Operating System | Windows 10, macOS 11, or Linux (Ubuntu 20.04) | Windows 11, macOS 13, or Linux (Ubuntu 22.04) | Windows 11 Pro, macOS 14, or Linux (Ubuntu 22.04) |

The development requirements are specified to accommodate the computational demands of training machine learning models, processing large environmental datasets, running multiple services simultaneously (frontend, backend, database), and executing Jupyter notebooks for exploratory data analysis. For end users accessing the deployed web application, the minimum requirements are sufficient as the majority of computation occurs on the server side. The GPU requirement is primarily relevant for development and experimentation with deep learning models; the deployed system does not require client-side GPU capabilities.

---

## 3.5 Data Gathering Procedures

This section describes the procedures employed to collect the information, datasets, and reference materials necessary for the design, development, and evaluation of LUMI.

### 3.5.1 Document Reviews

Document review was employed as a primary data gathering technique to establish the theoretical foundation, methodological framework, and domain knowledge required for the development of LUMI. The researchers systematically examined academic and professional literature to understand current practices, identify research gaps, and inform system design decisions.

The following categories of documents were reviewed:

**Research Papers and Academic Literature.** Peer-reviewed journal articles and conference papers were reviewed to understand the state of the art in renewable energy forecasting, environmental intelligence systems, and machine learning applications in the energy domain. These sources provided insights into algorithm selection, feature engineering strategies, and evaluation methodologies that were adapted for the Philippine context.

**Energy Forecasting Studies.** Existing studies on energy demand forecasting and renewable energy output prediction were examined to identify appropriate statistical and machine learning techniques. Particular attention was given to studies conducted in Southeast Asian contexts and island nations with climates and grid structures comparable to the Philippines.

**Renewable Energy Studies.** Literature on renewable energy adoption, site feasibility analysis, and multi-criteria decision-making was reviewed to inform the design of the recommendation engine. Studies examining public perception, economic factors, and technical criteria for renewable energy selection provided the basis for the rule-based and AI-assisted recommendation logic.

**Machine Learning Methodology References.** Textbooks and methodological papers on supervised learning, time-series analysis, deep learning, and model evaluation were consulted to ensure rigorous application of machine learning practices. These references guided the selection of appropriate metrics, validation strategies, and experimental designs for model testing.

**Government Energy Reports.** Official publications from the Philippine Department of Energy (DOE), the National Grid Corporation of the Philippines, and the Philippine Atmospheric, Geophysical and Astronomical Services Administration (PAGASA) were reviewed to identify available datasets, understand national energy statistics, and align the system's scope with official energy planning frameworks.

**Environmental Datasets Documentation.** Technical documentation accompanying climate datasets, elevation models, and geographic information system (GIS) data was reviewed to ensure correct interpretation and processing of environmental variables. This documentation was essential for the accurate integration of meteorological and topographic data into prediction models.

The insights gathered from document reviews directly informed the system architecture, algorithm selection, feature definitions, and evaluation criteria employed in LUMI. They also provided the evidentiary basis for the significance of the study and the design choices documented in this methodology.

### 3.5.2 Observation

Observation was employed as a qualitative data gathering technique during the testing and evaluation phases of system development. The researchers conducted structured observations of system behavior and user interactions to identify usability issues, assess response quality, and validate the practical utility of system outputs.

Observation was applied in the following contexts:

**System Testing Observation.** During functional and integration testing, researchers observed the system's behavior under various input conditions. This included monitoring the accuracy of data visualizations, the correctness of prediction outputs, the stability of API integrations, and the consistency of AI assistant responses. Observations were documented in structured logs to facilitate defect reporting and iterative improvement.

**User Interaction Evaluation.** Potential users were invited to interact with the system while researchers observed their navigation patterns, task completion efficiency, and areas of confusion. The researchers recorded observations regarding the intuitiveness of the dashboard layout, the clarity of visualization labels, and the ease of accessing forecasting and recommendation features.

**Dashboard Usage Observation.** Researchers observed how users interpreted energy trend visualizations, forecast charts, and geographic maps. Particular attention was given to whether users could correctly extract actionable insights from the presented data and whether the visual encoding of information (colors, scales, legends) supported accurate understanding.

**AI Assistant Interaction Observation.** The quality of AI assistant interactions was assessed through observation of user query patterns and the generated responses. Researchers observed whether the AI assistant correctly understood domain-specific questions, provided relevant and factually grounded answers, and maintained coherence across multi-turn conversations.

The following aspects were systematically observed and documented:

- **Usability Issues:** Identification of interface elements that caused confusion, navigation delays, or errors in user input.
- **Response Quality:** Assessment of AI assistant answers for factual correctness, relevance to the query, and completeness of information.
- **System Behavior:** Monitoring of unexpected system states, error messages, performance degradation, or inconsistent outputs.
- **Prediction Presentation:** Evaluation of whether forecast results and model outputs were presented in a manner that supported user understanding and decision-making.
- **User Difficulties:** Documentation of tasks that users struggled to complete, features that were difficult to locate, and terminology that required clarification.

Observation records were compiled and analyzed to generate actionable recommendations for interface refinements, workflow improvements, and additional user guidance features.

### 3.5.3 Testing Scripts and Code Validation

The researchers developed and executed testing scripts to validate the correctness, performance, and reliability of system components. These scripts provided systematic, repeatable methods for verifying functionality and detecting anomalies across the system's modules.

The following categories of testing scripts were created:

**Machine Learning Model Evaluation Scripts.** Scripts were developed to automate the evaluation of machine learning models using standard statistical metrics. These scripts loaded trained models, applied them to held-out test datasets, and computed performance indicators such as Mean Absolute Error (MAE), Mean Squared Error (MSE), Root Mean Square Error (RMSE), Mean Absolute Percentage Error (MAPE), and the coefficient of determination (R-squared). The scripts also generated diagnostic visualizations including residual plots and prediction versus actual value scatter plots.

**API Testing Scripts.** Backend API endpoints were validated using automated test scripts that verified correct HTTP response codes, response payload structure, data type consistency, and error handling behavior. These scripts tested authentication flows, data retrieval endpoints, prediction request handling, and AI assistant query processing under both normal and edge-case conditions.

**Backend Testing Scripts.** Unit test scripts were written to verify the correctness of individual functions and classes in the backend codebase. Integration test scripts validated the interactions between database layers, business logic modules, and external service clients. These tests ensured that data flows correctly through the system and that state changes occur as expected.

**Data Processing Validation Scripts.** Scripts were created to validate the integrity and correctness of data preprocessing pipelines. These scripts checked for data type conformance, missing value handling, outlier detection accuracy, and the correctness of feature engineering transformations. They also verified that processed datasets maintained referential integrity and statistical consistency with source data.

**System Functionality Testing Scripts.** End-to-end test scripts simulated complete user workflows, from region selection and data visualization to forecast generation and recommendation retrieval. These scripts validated that the integrated system produced coherent results across multiple modules and that user actions triggered the correct sequence of backend processes.

Examples of validation checks performed by testing scripts include:

- **Input Validation:** Verifying that the system rejects invalid or malformed inputs (e.g., out-of-range dates, unsupported regions, empty query strings) with appropriate error messages.
- **Prediction Accuracy Checking:** Comparing model outputs against known test values to ensure that predictions fall within expected ranges and that model drift is detected.
- **Response Time Measurement:** Recording the latency of API calls, model inference operations, and AI assistant response generation to ensure compliance with performance requirements.
- **Memory Utilization Monitoring:** Tracking memory consumption during data processing, model training, and concurrent user request handling to identify potential inefficiencies or memory leaks.
- **Error Handling:** Deliberately triggering error conditions (e.g., unavailable external APIs, missing database records, malformed data) to verify that the system responds gracefully and provides informative feedback.

These testing scripts were integrated into the development workflow and executed during each iteration to maintain system quality and facilitate regression detection.

---

## 3.6 System Development Procedures

This section describes the systematic workflow followed by the researchers in developing LUMI, from initial planning through architectural design and implementation.

### 3.6.1 Planning

The planning phase established the strategic and operational framework for the development of LUMI. During this phase, the researchers defined project objectives, identified data sources, selected technology stacks, and organized development tasks.

**Project Planning.** The researchers developed a project plan that outlined the major milestones, deliverables, and evaluation criteria for the study. The plan allocated time for literature review, dataset acquisition, prototype development, model training, system integration, testing, and documentation. Risk factors such as data availability, API reliability, and computational resource constraints were identified and mitigation strategies were formulated.

**Requirement Gathering.** Functional and non-functional requirements were gathered through review of existing environmental intelligence systems, analysis of Philippine energy sector needs, and consideration of the target user population. Requirements were prioritized based on their contribution to the study's objectives and their feasibility within the project timeline.

**Dataset Identification.** Publicly available datasets from the Philippine Department of Energy, climate monitoring agencies, and geographic data repositories were identified and catalogued. The researchers evaluated datasets for relevance, completeness, temporal coverage, and licensing terms. Data acquisition procedures including download protocols, API access requests, and extraction from published reports were established.

**Technology Selection.** The technology stack was selected based on the requirements for scalability, maintainability, and alignment with the researchers' technical competencies. Python was selected for backend and machine learning development due to its extensive ecosystem of scientific computing libraries. React with Tailwind CSS was selected for frontend development to ensure component reusability and responsive design. Supabase was selected for database services to leverage managed PostgreSQL with real-time capabilities. Google Gemini and Groq APIs were selected for AI assistant functionality based on their performance characteristics and integration support.

**Team and Task Organization.** Development responsibilities were distributed among team members according to expertise areas including frontend development, backend API development, machine learning engineering, data processing, and documentation. Regular coordination meetings were scheduled to synchronize progress, resolve blockers, and align on design decisions.

---

### 3.6.2 Software Design

#### 3.6.2.1 System Architecture

LUMI follows a layered architecture that separates concerns among data acquisition, processing, modeling, intelligence, and presentation layers. This architecture promotes modularity, maintainability, and scalability by ensuring that each layer can be developed, tested, and updated independently.

The data flow through the system follows a pipeline structure:

**Data Sources.** The foundation of LUMI is its integration of multiple data sources. These include Philippine Department of Energy statistical publications, climate and meteorological datasets, geographic and terrain data, and product cost information scraped from commercial platforms. External APIs provide real-time or periodic data updates where available.

**Data Processing.** Raw data from various sources is ingested into preprocessing pipelines that normalize formats, resolve inconsistencies, handle missing values, and engineer features suitable for machine learning. This layer also includes extraction, transformation, and loading (ETL) procedures for structured storage.

**Machine Learning Models.** Processed data is fed into machine learning and statistical models that perform forecasting and prediction tasks. This layer includes regression models for renewable energy potential estimation, time-series models for energy demand forecasting, and classification or ranking models for recommendation support.

**Prediction Layer.** Model outputs are aggregated, formatted, and enriched with metadata in the prediction layer. This layer manages model versioning, result caching, and the assembly of multi-model ensemble outputs where applicable.

**AI Decision Support Layer.** The AI decision support layer integrates large language model capabilities through the Google Gemini and Groq APIs. It processes natural language queries, retrieves relevant system data and knowledge context, and generates interpretive responses, recommendations, and scenario analyses.

**User Interface.** The presentation layer delivers the system's capabilities through an interactive web-based dashboard. Users can visualize data, explore forecasts, interact with the AI assistant, and receive recommendations through a responsive interface designed for accessibility and clarity.

This layered architecture ensures that changes at any level, such as swapping a machine learning model, updating a data source, or refining the AI assistant's prompt logic, can be implemented without destabilizing the entire system.

#### 3.6.2.2 Database Design

The database design supports the storage and efficient retrieval of the diverse data types utilized by LUMI. The relational database schema is organized around the following data domains:

**Energy Datasets.** Tables storing historical energy generation data, consumption statistics, and grid capacity information segmented by region, technology type, and time period. These tables maintain referential integrity with geographic dimension tables and support time-series queries for forecasting model training.

**Environmental Data.** Tables containing climate measurements including temperature, precipitation, solar irradiance, wind speed, and elevation data. Geographic identifiers link environmental records to specific Philippine regions, provinces, and municipalities to enable localized analysis.

**Model Outputs.** Tables dedicated to storing trained model metadata, hyperparameter configurations, training timestamps, and prediction results. These records support model versioning, performance tracking over time, and the reproduction of historical forecasts.

**User Interactions.** Tables recording user accounts, session activities, saved preferences, and query histories. This data supports personalized experiences and usage analytics while adhering to privacy considerations.

**AI Responses.** Tables capturing AI assistant query logs, generated responses, source references, and latency metrics. These records enable the evaluation of response quality, identification of common query patterns, and iterative improvement of prompt engineering strategies.

The database design employs normalization principles to minimize redundancy while maintaining query performance through appropriate indexing on frequently accessed columns such as geographic identifiers, timestamps, and foreign keys.

#### 3.6.2.3 Algorithm Structure

The following template structure is used to document the algorithms implemented within LUMI. Each algorithm is described in terms of its purpose, expected inputs, processing steps, and generated outputs.

---

**Algorithm Name:** [Algorithm Identifier]

**Purpose:** [Description of the problem the algorithm solves and its role within the system]

**Input:** [Description of expected input data including format, dimensions, and preprocessing requirements]

**Process:** [Step-by-step description of the algorithmic procedure, including mathematical operations, model inference steps, or logical rules applied]

**Output:** [Description of the generated output including format, units, and interpretation guidelines]

---

The following algorithms are implemented in LUMI:

**Data Preprocessing Algorithm.** [To be documented: Description of the pipeline for cleaning, normalizing, and transforming raw energy and environmental data into model-ready feature sets.]

**Renewable Energy Forecasting Algorithm.** [To be documented: Description of the machine learning or statistical approach used to predict renewable energy potential based on environmental inputs.]

**Energy Demand Forecasting Algorithm.** [To be documented: Description of the time-series modeling approach used to project future energy demand patterns.]

**Recommendation Generation Algorithm.** [To be documented: Description of the rule-based or AI-assisted approach used to generate personalized renewable energy recommendations based on user inputs and environmental conditions.]

---

#### 3.6.2.4 AI Tools and API

LUMI integrates large language model (LLM) capabilities through the Google Gemini API and the Groq API to provide AI-assisted decision support. These integrations enable the system to process natural language queries, interpret complex energy-related questions, and generate informative responses that complement the quantitative outputs of the machine learning and statistical modules.

**Purpose.** The AI assistant serves as an interactive decision support component that helps users understand renewable energy concepts, interpret forecast results, evaluate their options, and receive contextual recommendations. Unlike static reports, the AI assistant can engage in conversational exchanges, adapt its explanations to the user's level of technical expertise, and address questions that fall outside the predefined scope of the dashboard visualizations.

**Input/Output Flow.** The AI assistant receives natural language queries from users through the frontend interface. These queries are preprocessed to detect intent, extract relevant entities (e.g., region names, energy source types, time periods), and enrich the prompt with contextual data retrieved from the system's knowledge base. The enriched prompt is then transmitted to the Gemini or Groq API. The generated response is postprocessed to ensure formatting consistency, verify factual grounding against system data where applicable, and filter inappropriate content. The final response is delivered to the user through the chat interface.

**Role in Decision Support.** The AI assistant plays a complementary role to the quantitative prediction modules. While the forecasting models provide numerical projections of energy demand and renewable potential, the AI assistant interprets these projections in accessible language, explains the factors influencing the predictions, and guides users through what-if scenarios. For example, a user might ask why solar energy is recommended for a particular region; the AI assistant can synthesize information from climate data, geographic features, and cost estimates to provide a coherent explanation.

**Prompt Processing.** The system employs prompt engineering techniques to structure API inputs for optimal response quality. Prompts are designed to include system context, user query, relevant retrieved knowledge chunks from the vector database, and explicit instructions regarding response format, length, and tone. Chain-of-thought prompting may be used for complex reasoning tasks, while few-shot examples are included for structured output formats such as recommendation summaries.

**Response Generation.** The LLM generates responses by attending to the provided prompt context and leveraging its pretrained knowledge of energy, climate, and technology domains. Responses are streamed to the frontend where they are rendered in real time. The system maintains conversation history to support multi-turn interactions and contextual follow-up questions.

**Evaluation Considerations.** Evaluating LLM outputs requires approaches distinct from traditional classification accuracy metrics. Since the AI assistant generates free-text responses rather than discrete labels, its performance is assessed through the following dimensions:

- **Response Correctness:** Verification that factual claims in the response align with the system's underlying data and established domain knowledge.
- **Relevance:** Assessment of whether the response directly addresses the user's query and provides information that is useful for decision-making.
- **Ground Truth Comparison:** Comparison of responses against reference answers prepared by domain experts for a set of benchmark questions.
- **Expert Validation:** Human evaluation by energy practitioners or academic experts who rate responses on accuracy, completeness, and clarity using Likert scales or rubric-based scoring.
- **Hallucination Checking:** Detection of fabricated facts, unsupported claims, or contradictory statements in generated responses. This is performed through automated fact-checking against system data and manual review of sample outputs.
- **Response Time:** Measurement of end-to-end latency from query submission to response completion, ensuring that interactions remain fluid and usable.
- **Token and Resource Usage:** Monitoring of API token consumption and associated costs to ensure sustainable operation within project resource constraints.

The evaluation of the AI assistant will rely on benchmark question sets, expert review panels, and user feedback rather than traditional accuracy metrics such as precision or recall, which are not applicable to generative text tasks.

---

### 3.6.3 Testing Procedures

This section presents the testing and evaluation plans designed to verify the correctness, performance, and usability of LUMI. These plans are established prior to the execution of tests and serve as the methodological framework for systematic validation. Actual test results will be reported in subsequent chapters.

#### Machine Learning Model Testing

**Testing Objectives.** The primary objectives of machine learning model testing are to evaluate the predictive performance of forecasting and estimation models, compare the effectiveness of different algorithms, and ensure that models generalize well to unseen data. Testing also aims to validate that model outputs are stable, reproducible, and suitable for decision support.

**Metrics for Regression and Time-Series Tasks.** Since LUMI's forecasting modules predict continuous numerical values (e.g., energy demand in megawatts, renewable energy output potential), regression-oriented metrics are employed:

- **Mean Absolute Error (MAE):** The average absolute difference between predicted and actual values. MAE provides an intuitive measure of prediction error in the original units of the target variable.
- **Mean Squared Error (MSE):** The average squared difference between predicted and actual values. MSE penalizes larger errors more heavily than MAE, making it sensitive to significant deviations.
- **Root Mean Square Error (RMSE):** The square root of MSE, expressed in the original units of the target variable. RMSE is commonly used for comparing model performance across studies.
- **Mean Absolute Percentage Error (MAPE):** The average absolute percentage difference between predicted and actual values. MAPE facilitates comparison across datasets with different scales and is a standard metric in energy forecasting literature.
- **Coefficient of Determination (R-squared):** The proportion of variance in the dependent variable explained by the model. R-squared indicates the overall goodness of fit.

**Metrics for Classification Tasks (if applicable).** Should any component of LUMI involve classification (e.g., categorizing regions by renewable energy suitability levels), the following metrics would apply:

- **Accuracy:** The proportion of correctly classified instances out of the total instances.
- **Precision:** The proportion of true positive predictions among all positive predictions.
- **Recall:** The proportion of true positive predictions among all actual positive instances.
- **F1-Score:** The harmonic mean of precision and recall, providing a balanced measure of classification performance.

Classification metrics are not always appropriate for LUMI because the core forecasting tasks are formulated as regression problems predicting continuous energy output and demand values rather than discrete class labels. Applying classification metrics would require arbitrary binning of continuous predictions, which would lose granularity and potentially misrepresent model performance. Therefore, regression metrics are prioritized, with classification metrics reserved for any explicitly categorical subtasks that may be introduced.

**Validation Strategy.** Models are evaluated using train-test splits and time-series cross-validation to ensure that temporal ordering is respected and that models are tested on future periods not seen during training. This prevents data leakage and provides realistic estimates of forecasting accuracy.

#### Computational Performance Testing

Computational performance testing evaluates the efficiency and resource utilization of LUMI under representative operating conditions. The following metrics are measured:

- **Response Time:** The elapsed time between a user request (e.g., loading a forecast, submitting an AI query) and the completion of the system's response. Response time is measured at the API level and at the frontend level to identify bottlenecks.
- **Memory Utilization:** The amount of RAM consumed by the backend services, data processing pipelines, and model inference operations during peak and average load conditions. Memory profiling tools are used to detect leaks and inefficiencies.
- **CPU Utilization:** The percentage of CPU resources consumed during data processing, model training, and API request handling. CPU utilization is monitored to ensure that the system operates within acceptable limits and to identify computationally intensive operations that may require optimization.
- **Processing Time:** The time required to complete batch operations such as model training, dataset ingestion, and report generation. Processing time is distinguished from user-facing response time to assess backend efficiency.

Performance benchmarks are established by measuring each metric under controlled conditions with documented input sizes and request volumes. Baseline measurements are recorded for comparison against optimization efforts in subsequent iterations.

#### LLM Evaluation Testing

The evaluation of the Google Gemini and Groq API integrations requires specialized testing plans that account for the generative and nondeterministic nature of large language model outputs.

**Evaluation Plan.** A structured benchmark question set is prepared covering a range of query types including factual questions about renewable energy, interpretation of forecast results, recommendation requests, and clarification follow-ups. Each benchmark question has a reference answer prepared by the researchers based on system data and domain knowledge.

The following dimensions are measured:

- **Response Correctness:** Responses are scored on a Likert scale by expert evaluators for factual accuracy. Automated checks compare stated numerical values against the system's database where applicable.
- **Answer Relevance:** Evaluators assess whether the response addresses the user's intent and provides useful information for renewable energy decision-making. Irrelevant tangents and generic statements are flagged.
- **Groundedness:** The degree to which responses are grounded in the system's data and retrieved knowledge context rather than relying solely on the LLM's parametric knowledge. Groundedness is verified by inspecting the retrieved context chunks associated with each response.
- **Hallucination Rate:** The proportion of responses containing fabricated facts, unsupported numerical claims, or contradictory statements. Hallucinations are identified through manual review and cross-reference with authoritative data sources.
- **Expert Validation Score:** Domain experts rate overall response quality on a standardized rubric encompassing accuracy, completeness, clarity, and usefulness.
- **Response Latency:** The time from query submission to fully rendered response, measured in milliseconds. Latency is tested under varying prompt lengths and complexity levels.
- **Token Consumption:** The number of input and output tokens consumed per query is tracked to estimate API usage costs and optimize prompt efficiency.

**Appropriateness of Evaluation Approach.** Traditional classification accuracy is not applicable to LLM evaluation because the AI assistant does not select from a fixed set of labels. Instead, it generates open-ended text where correctness is multidimensional and context-dependent. The evaluation therefore relies on benchmark comparisons, rubric-based expert scoring, and user satisfaction metrics. This approach is consistent with established practices in natural language generation evaluation and acknowledges the inherent subjectivity in assessing text quality.

#### System Testing

System testing validates the integrated functionality of LUMI as a complete application. The following testing plans are established:

**Functional Testing.** Each functional requirement documented in Section 3.4.1 is mapped to one or more test cases. Test cases specify preconditions, input data, execution steps, and expected outcomes. Functional testing verifies that the system behaves correctly under normal operating conditions and handles edge cases appropriately.

**Integration Testing.** Integration testing verifies that the frontend, backend, database, and external services interact correctly. Test scenarios include end-to-end workflows such as user login, region selection, data retrieval, forecast generation, and AI assistant query handling. Integration tests identify interface mismatches, data serialization errors, and authentication failures.

**API Testing.** Backend API endpoints are tested for correctness of HTTP methods, response status codes, payload schema conformance, and error handling. Automated API tests verify that endpoints enforce authentication, validate input parameters, return consistent data types, and handle timeout and failure scenarios gracefully.

**User Acceptance Testing.** Potential users and domain experts are invited to perform predefined tasks using the system. Their ability to complete tasks successfully, the time required, and their subjective satisfaction are recorded. User acceptance testing provides qualitative validation of the system's practical utility and identifies usability improvements for future iterations.

#### Deployment Plan

The deployment plan outlines the strategy for making LUMI accessible to its intended users after successful testing and evaluation.

**Deployment Environment.** The frontend application is deployed as a static site to a cloud hosting platform (e.g., Netlify or Vercel) that provides content delivery network (CDN) distribution, automatic HTTPS, and continuous deployment from the version control repository. The backend services are deployed to a platform-as-a-service (PaaS) provider (e.g., Render, Railway, or AWS) that supports Python application hosting, environment variable management, and horizontal scaling.

**Hosting Setup.** The hosting environment is configured with separate production and staging instances. The staging instance serves as a pre-production environment for final validation before promoting changes to the production instance. Domain configuration, SSL certificates, and DNS records are established to ensure secure and accessible endpoints.

**Database Deployment.** The PostgreSQL database is hosted on Supabase, which provides managed database services, automatic backups, row-level security, and real-time subscriptions. Database migrations are version-controlled and applied through automated deployment pipelines to ensure schema consistency across environments.

**API Configuration.** External API keys for Google Gemini and Groq are stored as encrypted environment variables and are never committed to version control. API rate limits are monitored, and fallback logic is implemented to switch between providers or degrade gracefully when limits are approached.

**Security Considerations.** The system implements standard security practices including HTTPS enforcement, secure authentication using JSON Web Tokens (JWT), input sanitization, and parameterized database queries to prevent injection attacks. CORS policies are configured to restrict frontend access to authorized domains.

**Monitoring After Deployment.** Application logs, error traces, and performance metrics are collected through the hosting platform's monitoring tools. Alert thresholds are configured for high error rates, elevated response times, and memory usage spikes. Regular log reviews are conducted to identify and resolve issues proactively.

**Maintenance Plan.** A maintenance schedule is established for applying dependency updates, security patches, and model retraining. The model registry tracks model versions and performance history, enabling rollback to previous model versions if updated models exhibit degraded performance. Dataset refresh procedures are documented to ensure that the system's data remains current with new DOE publications and climate records.

---

*[End of Chapter 3]*
