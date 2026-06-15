CHAPTER 2

METHODOLOGY

This chapter outlines the methodological framework used to guide the development and evaluation of LUMI: Data-Driven Environmental Intelligence System for Renewable Energy Decision Support. It details the purpose of each development phase, the chosen software development model, and the procedures followed to ensure the system was built, tested, and validated effectively. The methodology serves as a structured approach to ensure the system meets its functional goals and user needs through systematic planning, implementation, and continuous improvement.

2.1. Purpose and Description

This section presents the overall methodological direction of the study. LUMI is developed as a web-based environmental intelligence platform that integrates machine learning forecasting models, statistical time-series analysis, environmental data processing, and AI-assisted decision support using large language models. The methodology covers all stages from initial concept to deployment, including data gathering, system design, development, testing, and evaluation.

2.1.1 Conceptual Model of the Study

[Figure placeholder: Conceptual Model of LUMI]

The conceptual model illustrates how LUMI operates as an integrated system. External data sources such as Department of Energy publications, climate datasets, and geographic information feed into the data processing layer. Processed data is then used by machine learning and statistical forecasting models to generate predictions. These predictions, together with user queries, are processed by the AI decision support layer powered by Google Gemini and Groq APIs. The results are presented to users through an interactive web-based dashboard that supports data visualization, forecast exploration, and conversational assistance.

2.1.2. Operational Definition of Terms

Data-Driven Environmental Intelligence: The application of data analysis, machine learning, and artificial intelligence techniques to process environmental and energy data in order to generate actionable insights for decision-making.

Renewable Energy Forecasting: The use of predictive models to estimate future energy generation potential from renewable sources such as solar, wind, and hydroelectric power based on historical data and environmental conditions.

Energy Demand Forecasting: The application of statistical and machine learning methods to project future electricity consumption patterns using historical demand data and influencing factors.

Large Language Model (LLM): A type of artificial intelligence model trained on vast text corpora capable of understanding and generating human-like natural language responses. In this study, LLMs are used through the Google Gemini API and Groq API to provide AI-assisted decision support.

AutoRegressive Integrated Moving Average (ARIMA): A statistical time-series forecasting method that models temporal dependencies in data to predict future values. It is used in LUMI for baseline energy demand forecasting.

Retrieval-Augmented Generation (RAG): A technique that enhances LLM responses by retrieving relevant contextual information from a knowledge base before generating answers. LUMI employs RAG to ground AI assistant responses in system data.

Vector Database (FAISS): A data structure optimized for storing and searching high-dimensional vector embeddings. LUMI uses FAISS to enable semantic search over energy-related documents for the AI assistant.

2.2. Research Design

The study used a descriptive and developmental research design. Data were gathered through document reviews, system observations, testing scripts, and expert consultations to inform the design, development, and validation of the platform. The developmental aspect involved the systematic construction of a web-based environmental intelligence system using iterative development cycles.

To evaluate the platform's forecasting accuracy, performance, and overall effectiveness, the researchers applied multiple assessment tools. Machine learning model performance was evaluated using standard regression metrics including Mean Absolute Error (MAE), Root Mean Square Error (RMSE), Mean Absolute Percentage Error (MAPE), and R-squared. Computational performance was assessed through response time, memory utilization, and CPU utilization measurements. For the AI assistant component, evaluation relied on benchmark questions, expert validation, and rubric-based scoring rather than traditional classification accuracy, given the generative nature of large language model outputs.

2.3. Participants or Respondents

The participants of this study include individuals from communities, households, and academic institutions who represent the platform's primary target users. These participants possess varying levels of technical knowledge, from general users seeking to understand renewable energy options to students and researchers interested in energy forecasting and environmental data analysis.

In addition, energy practitioners, government agency representatives, and academic faculty are included to provide insights on the platform's data quality, forecasting reliability, usability, and alignment with industry and policy expectations.

These participants are involved in various stages of evaluation, including system observation, usability testing, and expert validation, which help validate the platform's design, effectiveness, and overall user experience.

2.4.Project Development Methodology (Software Development Life Cycle)

Figure 2. Iterative and Incremental Development

For this project, the researchers adopted the Iterative and Incremental Development approach. This model allows the system to be built progressively through repeated cycles (iterations) and in smaller portions (increments), enabling continuous improvement based on testing feedback and stakeholder input. Each cycle adds functional components, allowing earlier evaluation, faster error detection, and greater flexibility throughout the development process.

By using this approach, the system could be refined at every stage, starting from initial planning, to development, testing, and ongoing revisions, ensuring alignment with user needs, project goals, and technical feasibility. The complex nature of LUMI, which integrates machine learning forecasting, environmental data processing, statistical analysis, AI-assisted decision support, and interactive visualization, makes the iterative model particularly suitable. Machine learning development is inherently experimental, requiring repeated cycles of model training, evaluation, and refinement. The incremental approach allows core functionalities such as data ingestion and preprocessing to be developed and validated independently before integrating more advanced features like AI assistant integration and recommendation generation.

The following phases describe the structured activities conducted within each iteration of the development cycle. The exact timeline and scheduling of these phases are subject to finalization based on project milestones and academic requirements.

Phase 1: Planning
In the initial planning phase, the researchers gathered system requirements and studied existing environmental intelligence platforms and renewable energy decision support tools to identify key features and design patterns. The team reviewed publicly available energy datasets from the Philippine Department of Energy and climate data sources to assess their relevance, completeness, and accessibility. A modular structure was planned to allow isolated development of each feature and ensure easier integration.

The programmers reviewed the programming languages, frameworks, and tools required for implementation. Python was selected for backend development and machine learning due to its extensive ecosystem of scientific libraries. React with Tailwind CSS was chosen for the frontend to ensure component reusability and responsive design. Supabase was selected for database services, while Google Gemini and Groq APIs were identified for AI assistant functionality.

The documentation team collected academic references on renewable energy forecasting, environmental intelligence systems, machine learning methodologies, and statistical time-series analysis. Initial test plans were drafted and reviewed with the developer for alignment. Roles were assigned based on individual strengths and expertise. The project manager ensured that all planning tasks progressed on time and remained coordinated across the team.

Phase 2: Requirements Analysis
During the requirements phase, the researchers conducted an in-depth investigation into the key functions and scope expected of an environmental intelligence system for renewable energy decision support. This process involved analyzing existing platforms and identifying essential features that define an effective and data-driven learning experience.

The team documented functional requirements using formal "shall" statements to ensure clarity and testability. These requirements covered user interaction, renewable energy forecasting, energy demand forecasting, data ingestion and preprocessing, machine learning prediction modules, statistical forecasting modules, AI assistant integration, API interaction, visualization and dashboard, reports and recommendations, model results display, data storage, and deployment access.

Throughout the development process, the team continuously gathers and documents new requirements derived from user feedback, expert consultation, and ongoing project developments. Each new input is carefully evaluated and thoughtfully integrated into the planning and design phases to ensure the system remains responsive, adaptive, and aligned with the evolving goals of the project.

Phase 3: System Design
To better design the platform, the researchers grounded their architectural decisions from document reviews and an analysis of existing environmental intelligence systems. These efforts provided a clearer understanding of what target users expect from a modern renewable energy decision support environment, and what the literature indicates are the most effective strategies for presenting energy data and forecasts to non-technical audiences.

Given that the target users include households, community members, students, and government institutions, the platform is developed with the assumption that users have varying levels of technical expertise. The system is designed to start with accessible data visualizations and guided insights, transitioning to more detailed forecasts and AI-assisted explanations for users who require deeper analysis.

The design incorporates a layered architecture comprising data sources, data processing, machine learning models, prediction layer, AI decision support layer, and user interface. This modular structure ensures that changes at any level can be implemented without destabilizing the entire system. Database schemas were designed to store energy datasets, environmental data, model outputs, user interactions, and AI responses. User interface mockups were created to establish the layout early, reducing design-related workload during later development.

Phase 4: Development / Implementation
During the implementation phase, the system was developed incrementally based on the finalized design and modular structure. The programmers focused on building core functionalities for each module, including data ingestion pipelines, preprocessing utilities, machine learning forecasting models, statistical time-series analysis, backend APIs, frontend dashboard components, and AI assistant integration.

Frontend components were built using React, Tailwind CSS, and Vite, while backend logic was implemented in Python using FastAPI. Supabase was utilized for structured data storage and user management. Machine learning models were trained using scikit-learn, statsmodels, and PyTorch on Philippine energy and environmental datasets. The Google Gemini and Groq APIs were integrated to provide natural language query processing and decision support.

As each module was implemented, the team conducted continuous testing to ensure stability and functionality. Unit testing and system testing were performed by the researchers using multiple devices to assess compatibility and performance. Identified issues were immediately documented and resolved before proceeding to the next cycle of development.

Phase 5: Testing
The testing phase involved verifying the functionality, stability, and accuracy of the system. The researchers conducted multiple levels of testing, including unit testing, integration testing, system testing, and machine learning model evaluation. These tests ensured that each module worked as intended and that the platform was responsive, accessible, and free of critical errors.

Machine learning models were evaluated using held-out test datasets and statistical metrics including MAE, MSE, RMSE, MAPE, and R-squared. API endpoints were tested for correctness, response time, and error handling. The AI assistant was evaluated through benchmark questions and expert validation. Issues found during testing were documented and resolved before proceeding to the next phase.

Phase 6: Evaluation
Following the completion of testing, the system underwent structured evaluation to measure its overall quality and effectiveness. Machine learning prediction accuracy was evaluated using appropriate statistical metrics. Computational performance was assessed through response time, memory utilization, and CPU utilization measurements.

The AI assistant's responses were evaluated on dimensions including correctness, relevance, groundedness, hallucination rate, expert validation score, response latency, and token consumption. This evaluation relied on benchmark question sets and human expert review rather than traditional classification accuracy, which is not applicable to generative text tasks. An acceptability evaluation was also conducted to gather feedback on the system's visual design, clarity, and user engagement.

Phase 7: Deployment
In the deployment phase, the system was launched in a controlled environment for demonstration and testing purposes. The frontend application was deployed as a static site to a cloud hosting platform that provides content delivery network distribution and automatic HTTPS. The backend services were deployed to a platform-as-a-service provider supporting Python application hosting.

The database was hosted on Supabase, which provides managed PostgreSQL services, automatic backups, and real-time subscriptions. External API keys for Google Gemini and Groq were configured as encrypted environment variables. Security measures including HTTPS enforcement, JWT authentication, input sanitization, and parameterized queries were implemented.

As part of the deployment process, researchers conducted a pilot run with selected participants. Participants were invited to interact with the platform, explore key modules, and provide feedback on usability and functionality. Observations from this pilot deployment were recorded to identify final areas for refinement.

2.5. Requirements Specifications: Tools, Technologies, or Platforms Used

This section outlines the key software, hardware, programming languages, frameworks, and platforms needed to develop and run LUMI. In addition, it offers a clear view of the technical environment, helping the development team and stakeholders stay aligned on the tools and resources that will support the system's overall functionality.

2.5.1. Functional Requirements

The system shall provide a user-friendly web interface that allows users to navigate between modules including the climate and energy dashboard, forecasting tools, recommendation engine, and AI assistant.

The system shall support user authentication and session management to ensure secure access to personalized features and saved preferences.

The system shall allow users to select Philippine regions and localities to receive localized energy and environmental insights.

The system shall implement machine learning models capable of forecasting renewable energy potential for solar, wind, and hydroelectric sources based on historical and environmental data.

The system shall display forecasted renewable energy output with appropriate confidence intervals and temporal granularity.

The system shall implement statistical time-series forecasting models to predict future energy demand trends based on historical consumption patterns.

The system shall present energy demand forecasts through interactive visualizations that allow users to explore projections across different time horizons.

The system shall ingest publicly available energy datasets from the Department of Energy (DOE) and environmental datasets from relevant Philippine government agencies.

The system shall support automated data retrieval from external APIs and manual import of structured datasets in standard formats such as CSV and JSON.

The system shall implement data preprocessing pipelines that handle missing values, outlier detection, data normalization, and feature engineering prior to model training.

The system shall validate incoming data for format consistency, completeness, and integrity before processing.

The system shall implement supervised learning algorithms for regression tasks related to energy output and demand prediction.

The system shall provide functionality for model training, hyperparameter tuning, cross-validation, and performance evaluation.

The system shall store trained model artifacts and metadata in a versioned manner to support reproducibility and comparison.

The system shall implement statistical forecasting techniques such as AutoRegressive Integrated Moving Average (ARIMA) and related time-series methods for baseline comparison and trend analysis.

The system shall generate forecast outputs with diagnostic plots including residual analysis and autocorrelation functions.

The system shall integrate an AI assistant capable of interpreting user queries related to renewable energy, climate data, and energy demand.

The system shall process natural language inputs and generate informative, contextually relevant responses based on system data and retrieved knowledge.

The system shall interface with the Google Gemini API and Groq API to leverage large language model capabilities for decision support and recommendation generation.

The system shall implement prompt engineering strategies to ensure that API inputs are structured for optimal response quality and relevance.

The system shall handle API errors, rate limits, and fallback mechanisms to maintain service availability.

The system shall provide interactive data visualizations including charts, graphs, and maps to represent climate patterns, energy trends, and forecast results.

The system shall implement a responsive dashboard layout that adapts to various screen sizes and devices.

The system shall generate structured reports summarizing energy forecasts, renewable energy potential assessments, and recommendation rationales.

The system shall present recommendation outputs in a clear, actionable format suitable for non-technical users.

The system shall display model performance metrics, prediction results, and comparative analyses in an interpretable format.

The system shall provide model explanation features that highlight key factors influencing predictions.

The system shall persistently store energy datasets, environmental data, model outputs, user interactions, and AI assistant responses in a structured database.

The system shall implement data access controls to ensure the security and privacy of stored information.

The system shall be deployable as a web application accessible through standard internet browsers without requiring specialized client software.

The system shall provide consistent performance and availability within the constraints of the chosen deployment platform.

2.5.2. Software Requirements

Table 1.
Software Requirements Table

| Category | Tool / Technology | Purpose | Usage in LUMI |
|----------|-----------------|---------|---------------|
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

2.5.3. Hardware Requirements

Table 2.
Hardware Requirements Table

| Category | Minimum Requirement | Recommended Requirement | Development Requirement |
|----------|---------------------|------------------------|------------------------|
| Processor | Intel Core i3 or AMD Ryzen 3 (quad-core, 2.0 GHz) | Intel Core i5 or AMD Ryzen 5 (hexa-core, 2.5 GHz) | Intel Core i7 or AMD Ryzen 7 (octa-core, 2.8 GHz) |
| Memory | 8 GB DDR4 | 16 GB DDR4 | 32 GB DDR4 |
| Hard Disk | 256 GB SSD | 512 GB SSD | 1 TB SSD |
| GPU | Integrated graphics (sufficient for web rendering) | Dedicated GPU with 4 GB VRAM (for accelerated ML training) | NVIDIA GPU with CUDA support, 8 GB+ VRAM (for deep learning experimentation) |
| Internet Connection | Stable broadband connection (5 Mbps) | High-speed broadband connection (25 Mbps) | High-speed broadband connection (50 Mbps or higher) |
| Operating System | Windows 10, macOS 11, or Linux (Ubuntu 20.04) | Windows 11, macOS 13, or Linux (Ubuntu 22.04) | Windows 11 Pro, macOS 14, or Linux (Ubuntu 22.04) |

The development requirements are specified to accommodate the computational demands of training machine learning models, processing large environmental datasets, running multiple services simultaneously (frontend, backend, database), and executing Jupyter notebooks for exploratory data analysis. For end users accessing the deployed web application, the minimum requirements are sufficient as the majority of computation occurs on the server side. The GPU requirement is primarily relevant for development and experimentation with deep learning models; the deployed system does not require client-side GPU capabilities.

2.6. Data Gathering Procedures

2.6.3. Document Reviews

To support the development and contextual relevance of the platform, the researchers conducted a review of academic literature, institutional materials, and government reports related to renewable energy, environmental intelligence, energy forecasting, and machine learning applications in the energy domain. This included research papers, energy forecasting studies, renewable energy studies, machine learning methodology references, government energy reports, and environmental datasets documentation published between 2021 and 2025.

Peer-reviewed journal articles and conference papers were reviewed to understand the state of the art in renewable energy forecasting, environmental intelligence systems, and machine learning applications in the energy domain. These sources provided insights into algorithm selection, feature engineering strategies, and evaluation methodologies that were adapted for the Philippine context.

Existing studies on energy demand forecasting and renewable energy output prediction were examined to identify appropriate statistical and machine learning techniques. Particular attention was given to studies conducted in Southeast Asian contexts and island nations with climates and grid structures comparable to the Philippines.

Literature on renewable energy adoption, site feasibility analysis, and multi-criteria decision-making was reviewed to inform the design of the recommendation engine. Studies examining public perception, economic factors, and technical criteria for renewable energy selection provided the basis for the rule-based and AI-assisted recommendation logic.

Textbooks and methodological papers on supervised learning, time-series analysis, deep learning, and model evaluation were consulted to ensure rigorous application of machine learning practices. These references guided the selection of appropriate metrics, validation strategies, and experimental designs for model testing.

Official publications from the Philippine Department of Energy (DOE), the National Grid Corporation of the Philippines, and the Philippine Atmospheric, Geophysical and Astronomical Services Administration (PAGASA) were reviewed to identify available datasets, understand national energy statistics, and align the system's scope with official energy planning frameworks.

Technical documentation accompanying climate datasets, elevation models, and geographic information system (GIS) data was reviewed to ensure correct interpretation and processing of environmental variables. This documentation was essential for the accurate integration of meteorological and topographic data into prediction models.

The insights gathered from document reviews directly informed the system architecture, algorithm selection, feature definitions, and evaluation criteria employed in LUMI. They also provided the evidentiary basis for the significance of the study and the design choices documented in this methodology.

2.6.4. Observation

Observation was used as a method to analyze user interaction with the platform during the testing phase. Selected participants were observed as they navigated the system's features, explored the dashboard, interpreted forecast visualizations, and interacted with the AI assistant. The researchers took note of usability issues, confusion points, and behavioral patterns.

During system testing, researchers observed the system's behavior under various input conditions. This included monitoring the accuracy of data visualizations, the correctness of prediction outputs, the stability of API integrations, and the consistency of AI assistant responses. Observations were documented in structured logs to facilitate defect reporting and iterative improvement.

During user interaction evaluation, potential users were invited to interact with the system while researchers observed their navigation patterns, task completion efficiency, and areas of confusion. The researchers recorded observations regarding the intuitiveness of the dashboard layout, the clarity of visualization labels, and the ease of accessing forecasting and recommendation features.

During dashboard usage observation, researchers observed how users interpreted energy trend visualizations, forecast charts, and geographic maps. Particular attention was given to whether users could correctly extract actionable insights from the presented data and whether the visual encoding of information (colors, scales, legends) supported accurate understanding.

During AI assistant interaction observation, the quality of AI assistant interactions was assessed through observation of user query patterns and the generated responses. Researchers observed whether the AI assistant correctly understood domain-specific questions, provided relevant and factually grounded answers, and maintained coherence across multi-turn conversations.

The following aspects were systematically observed and documented: usability issues, including identification of interface elements that caused confusion, navigation delays, or errors in user input; response quality, encompassing assessment of AI assistant answers for factual correctness, relevance to the query, and completeness of information; system behavior, monitoring unexpected system states, error messages, performance degradation, or inconsistent outputs; prediction presentation, evaluating whether forecast results and model outputs were presented in a manner that supported user understanding and decision-making; and user difficulties, documenting tasks that users struggled to complete, features that were difficult to locate, and terminology that required clarification.

Observation records were compiled and analyzed to generate actionable recommendations for interface refinements, workflow improvements, and additional user guidance features.

2.6.5. Testing Scripts / Code

To ensure system reliability, accuracy, and functionality, the researchers conducted a series of internal tests using pre-written scripts and manual walkthroughs. The testing process included debugging, validating logic flows, and checking system components such as data processing pipelines, machine learning model inference, API responses, and interactive modules. Functional testing and basic unit testing were applied to identify errors and verify expected outputs. The test results guided refinements and adjustments to the platform's backend and user interface before pilot deployment. All code-related changes were documented and version-controlled for traceability.

The following categories of testing scripts were created. Machine learning model evaluation scripts were developed to automate the evaluation of machine learning models using standard statistical metrics. These scripts loaded trained models, applied them to held-out test datasets, and computed performance indicators such as Mean Absolute Error (MAE), Mean Squared Error (MSE), Root Mean Square Error (RMSE), Mean Absolute Percentage Error (MAPE), and the coefficient of determination (R-squared). The scripts also generated diagnostic visualizations including residual plots and prediction versus actual value scatter plots.

API testing scripts were used to validate backend API endpoints. Automated test scripts verified correct HTTP response codes, response payload structure, data type consistency, and error handling behavior. These scripts tested authentication flows, data retrieval endpoints, prediction request handling, and AI assistant query processing under both normal and edge-case conditions.

Backend testing scripts included unit test scripts written to verify the correctness of individual functions and classes in the backend codebase. Integration test scripts validated the interactions between database layers, business logic modules, and external service clients. These tests ensured that data flows correctly through the system and that state changes occur as expected.

Data processing validation scripts were created to validate the integrity and correctness of data preprocessing pipelines. These scripts checked for data type conformance, missing value handling, outlier detection accuracy, and the correctness of feature engineering transformations. They also verified that processed datasets maintained referential integrity and statistical consistency with source data.

System functionality testing scripts simulated complete user workflows, from region selection and data visualization to forecast generation and recommendation retrieval. These scripts validated that the integrated system produced coherent results across multiple modules and that user actions triggered the correct sequence of backend processes.

Examples of validation checks performed by testing scripts include input validation, verifying that the system rejects invalid or malformed inputs (e.g., out-of-range dates, unsupported regions, empty query strings) with appropriate error messages; prediction accuracy checking, comparing model outputs against known test values to ensure that predictions fall within expected ranges and that model drift is detected; response time measurement, recording the latency of API calls, model inference operations, and AI assistant response generation to ensure compliance with performance requirements; memory utilization monitoring, tracking memory consumption during data processing, model training, and concurrent user request handling to identify potential inefficiencies or memory leaks; and error handling, deliberately triggering error conditions (e.g., unavailable external APIs, missing database records, malformed data) to verify that the system responds gracefully and provides informative feedback.

2.7. System Development Procedures

2.7.1.Planning

Project Schedule: Gantt Chart

[Figure placeholder: Gantt Chart of LUMI - Phase 1]

[Figure placeholder: Gantt Chart of LUMI - Phase 2]

Feasibility Study

Development and Operational Cost
The projected cost of the system remains highly practical due to the reliance on free-tier services for hosting, server maintenance, and frameworks. These free plans are sufficient for the initial deployment and pilot testing of the platform. In the event of scaling or exceeding usage limits, potential expenses may include Supabase for online database services, Netlify or Vercel for frontend hosting, and Render or Railway for backend deployment. Even with these possible upgrades, the total operational costs remain minimal compared to typical enterprise-level platforms, ensuring financial manageability and sustainability.

Project Planning
The researchers developed a project plan that outlined the major milestones, deliverables, and evaluation criteria for the study. The plan allocated time for literature review, dataset acquisition, prototype development, model training, system integration, testing, and documentation. Risk factors such as data availability, API reliability, and computational resource constraints were identified and mitigation strategies were formulated.

Requirement Gathering
Functional and non-functional requirements were gathered through review of existing environmental intelligence systems, analysis of Philippine energy sector needs, and consideration of the target user population. Requirements were prioritized based on their contribution to the study's objectives and their feasibility within the project timeline.

Dataset Identification
Publicly available datasets from the Philippine Department of Energy, climate monitoring agencies, and geographic data repositories were identified and catalogued. The researchers evaluated datasets for relevance, completeness, temporal coverage, and licensing terms. Data acquisition procedures including download protocols, API access requests, and extraction from published reports were established.

Technology Selection
The technology stack was selected based on the requirements for scalability, maintainability, and alignment with the researchers' technical competencies. Python was selected for backend and machine learning development due to its extensive ecosystem of scientific computing libraries. React with Tailwind CSS was selected for frontend development to ensure component reusability and responsive design. Supabase was selected for database services to leverage managed PostgreSQL with real-time capabilities. Google Gemini and Groq APIs were selected for AI assistant functionality based on their performance characteristics and integration support.

Team and Task Organization
Development responsibilities were distributed among team members according to expertise areas including frontend development, backend API development, machine learning engineering, data processing, and documentation. Regular coordination meetings were scheduled to synchronize progress, resolve blockers, and align on design decisions.

2.7.2.Software Design

Conceptual Design

[Figure placeholder: Conceptual Design of LUMI]

LUMI is designed as a web-based environmental intelligence platform that integrates data-driven forecasting, AI-assisted recommendations, and interactive visualization. The system follows a layered architecture that separates concerns among data acquisition, processing, modeling, intelligence, and presentation layers.

The data flow through the system follows a pipeline structure. Data Sources form the foundation of LUMI, integrating multiple data sources including Philippine Department of Energy statistical publications, climate and meteorological datasets, geographic and terrain data, and product cost information. External APIs provide real-time or periodic data updates where available.

Data Processing receives raw data from various sources through preprocessing pipelines that normalize formats, resolve inconsistencies, handle missing values, and engineer features suitable for machine learning. This layer also includes extraction, transformation, and loading procedures for structured storage.

Machine Learning Models receive processed data and perform forecasting and prediction tasks. This layer includes regression models for renewable energy potential estimation, time-series models for energy demand forecasting, and classification or ranking models for recommendation support.

The Prediction Layer aggregates, formats, and enriches model outputs with metadata. This layer manages model versioning, result caching, and the assembly of multi-model ensemble outputs where applicable.

The AI Decision Support Layer integrates large language model capabilities through the Google Gemini and Groq APIs. It processes natural language queries, retrieves relevant system data and knowledge context, and generates interpretive responses, recommendations, and scenario analyses.

The User Interface delivers the system's capabilities through an interactive web-based dashboard. Users can visualize data, explore forecasts, interact with the AI assistant, and receive recommendations through a responsive interface designed for accessibility and clarity.

This layered architecture ensures that changes at any level, such as swapping a machine learning model, updating a data source, or refining the AI assistant's prompt logic, can be implemented without destabilizing the entire system.

Technical Design

Context Data Flow Diagram

[Figure placeholder: Context Data Flow Diagram of LUMI]

This figure presents the Context Data Flow Diagram of LUMI, representing an early-stage prototype of the system. It provides a high-level overview of how the system interacts with external entities, namely the users (seeking renewable energy insights) and the admin (researchers managing the system).

[Figure placeholders: Top-Down Data Flow Diagram, Logical DFDs, Physical DFDs]

Entity Relationship Diagram

[Figure placeholder: Entity Relationship Diagram of LUMI]

Database Design

The database design supports the storage and efficient retrieval of the diverse data types utilized by LUMI. The relational database schema is organized around the following data domains.

Energy Datasets: Tables storing historical energy generation data, consumption statistics, and grid capacity information segmented by region, technology type, and time period. These tables maintain referential integrity with geographic dimension tables and support time-series queries for forecasting model training.

Environmental Data: Tables containing climate measurements including temperature, precipitation, solar irradiance, wind speed, and elevation data. Geographic identifiers link environmental records to specific Philippine regions, provinces, and municipalities to enable localized analysis.

Model Outputs: Tables dedicated to storing trained model metadata, hyperparameter configurations, training timestamps, and prediction results. These records support model versioning, performance tracking over time, and the reproduction of historical forecasts.

User Interactions: Tables recording user accounts, session activities, saved preferences, and query histories. This data supports personalized experiences and usage analytics while adhering to privacy considerations.

AI Responses: Tables capturing AI assistant query logs, generated responses, source references, and latency metrics. These records enable the evaluation of response quality, identification of common query patterns, and iterative improvement of prompt engineering strategies.

The database design employs normalization principles to minimize redundancy while maintaining query performance through appropriate indexing on frequently accessed columns such as geographic identifiers, timestamps, and foreign keys.

Data Dictionary

[Table placeholders for data dictionaries: Energy Data Directory, Environmental Data Directory, Model Output Directory, User Interaction Directory, AI Response Directory]

System Flow Chart

[Figure placeholder: User Flow Chart]

[Figure placeholder: Admin Flow Chart]

2.7.2.2.8.Algorithm Structure

The following template structure is used to document the algorithms implemented within LUMI. Each algorithm is described in terms of its purpose, expected inputs, processing steps, and generated outputs.

Algorithm Name: [Algorithm Identifier]

Purpose: [Description of the problem the algorithm solves and its role within the system]

Input: [Description of expected input data including format, dimensions, and preprocessing requirements]

Process: [Step-by-step description of the algorithmic procedure, including mathematical operations, model inference steps, or logical rules applied]

Output: [Description of the generated output including format, units, and interpretation guidelines]

The following algorithms are implemented in LUMI:

Data Preprocessing Algorithm: [To be documented: Description of the pipeline for cleaning, normalizing, and transforming raw energy and environmental data into model-ready feature sets.]

Renewable Energy Forecasting Algorithm: [To be documented: Description of the machine learning or statistical approach used to predict renewable energy potential based on environmental inputs.]

Energy Demand Forecasting Algorithm: [To be documented: Description of the time-series modeling approach used to project future energy demand patterns.]

Recommendation Generation Algorithm: [To be documented: Description of the rule-based or AI-assisted approach used to generate personalized renewable energy recommendations based on user inputs and environmental conditions.]

2.7.2.2.9.AI Tools and API

Google Gemini API

Google Gemini API was integrated into LUMI to provide natural language understanding and generation capabilities for the AI assistant component. The API processes user queries related to renewable energy, climate data, and energy demand, and generates informative responses that complement the quantitative outputs of the machine learning and statistical modules.

The AI assistant serves as an interactive decision support component that helps users understand renewable energy concepts, interpret forecast results, evaluate their options, and receive contextual recommendations. Unlike static reports, the AI assistant can engage in conversational exchanges, adapt its explanations to the user's level of technical expertise, and address questions that fall outside the predefined scope of the dashboard visualizations.

The AI assistant receives natural language queries from users through the frontend interface. These queries are preprocessed to detect intent, extract relevant entities (e.g., region names, energy source types, time periods), and enrich the prompt with contextual data retrieved from the system's knowledge base. The enriched prompt is then transmitted to the Gemini API. The generated response is postprocessed to ensure formatting consistency, verify factual grounding against system data where applicable, and filter inappropriate content. The final response is delivered to the user through the chat interface.

The AI assistant plays a complementary role to the quantitative prediction modules. While the forecasting models provide numerical projections of energy demand and renewable potential, the AI assistant interprets these projections in accessible language, explains the factors influencing the predictions, and guides users through what-if scenarios. For example, a user might ask why solar energy is recommended for a particular region; the AI assistant can synthesize information from climate data, geographic features, and cost estimates to provide a coherent explanation.

The system employs prompt engineering techniques to structure API inputs for optimal response quality. Prompts are designed to include system context, user query, relevant retrieved knowledge chunks from the vector database, and explicit instructions regarding response format, length, and tone. Chain-of-thought prompting may be used for complex reasoning tasks, while few-shot examples are included for structured output formats such as recommendation summaries.

Groq API

Groq API was integrated as an alternative and complementary large language model inference provider for the AI assistant features. Groq provides high-performance inference capabilities that can be used to process user queries when the primary API is unavailable or when comparative response generation is needed. The integration follows the same input-output flow as the Gemini API, with queries being preprocessed, enriched with context, and postprocessed before delivery to the user.

The system handles API errors, rate limits, and fallback mechanisms to maintain service availability. When one API provider experiences downtime or rate limiting, the system can automatically switch to the alternative provider, ensuring continuous AI assistant functionality.

Evaluating LLM outputs requires approaches distinct from traditional classification accuracy metrics. Since the AI assistant generates free-text responses rather than discrete labels, its performance is assessed through the following dimensions: response correctness, verifying that factual claims align with system data and established domain knowledge; relevance, assessing whether the response directly addresses the user's query and provides useful information for decision-making; ground truth comparison, comparing responses against reference answers prepared by domain experts for a set of benchmark questions; expert validation, where energy practitioners or academic experts rate responses on accuracy, completeness, and clarity using Likert scales or rubric-based scoring; hallucination checking, detecting fabricated facts, unsupported claims, or contradictory statements in generated responses through automated fact-checking against system data and manual review of sample outputs; response time, measuring end-to-end latency from query submission to response completion to ensure interactions remain fluid and usable; and token and resource usage, monitoring API token consumption and associated costs to ensure sustainable operation within project resource constraints.

The evaluation of the AI assistant relies on benchmark question sets, expert review panels, and user feedback rather than traditional accuracy metrics such as precision or recall, which are not applicable to generative text tasks.

2.7.3. Testing Procedures

System Test Plan

Table 3.
LUMI System Test Plan

| Aspect | Description |
|--------|-------------|
| Objective | Stress test the system to ensure robustness under multitasking conditions. Test all modules significant for forecasting accuracy, AI assistant quality, and visualization performance. Ensure the system is ready before releasing it to users. |
| Test Scope | The test covers core functionalities of the environmental intelligence platform, including user interface, data processing pipelines, machine learning forecasting modules, AI assistant integration, and performance under normal usage. |
| Testing Approach | The testing environment consists of the researchers' personal laptops and desktop computers, each configured to simulate various user conditions. The system is deployed across multiple devices to observe its behavior in different operating systems, browsers, and screen resolutions. This setup allows for a controlled yet diverse testing scenario, ensuring that the platform's performance remains stable and consistent across different hardware and software environments. |
| Test Environment | The testing is conducted internally by the researchers, using individual accounts to simulate multiple user experiences. Each researcher performs repeated testing cycles to evaluate the system's responsiveness, reliability, and overall functionality. Features are tested under various usage scenarios, including different user roles and interactions. The repeated trials aim to identify bugs, compatibility issues, and performance bottlenecks before the platform is released to a wider audience. |

Machine Learning Model Testing

The primary objectives of machine learning model testing are to evaluate the predictive performance of forecasting and estimation models, compare the effectiveness of different algorithms, and ensure that models generalize well to unseen data. Testing also aims to validate that model outputs are stable, reproducible, and suitable for decision support.

Since LUMI's forecasting modules predict continuous numerical values (e.g., energy demand in megawatts, renewable energy output potential), regression-oriented metrics are employed. Mean Absolute Error (MAE) provides the average absolute difference between predicted and actual values, offering an intuitive measure of prediction error in the original units of the target variable. Mean Squared Error (MSE) represents the average squared difference between predicted and actual values, penalizing larger errors more heavily than MAE. Root Mean Square Error (RMSE) is the square root of MSE, expressed in the original units of the target variable, and is commonly used for comparing model performance across studies. Mean Absolute Percentage Error (MAPE) represents the average absolute percentage difference between predicted and actual values, facilitating comparison across datasets with different scales. The coefficient of determination (R-squared) indicates the proportion of variance in the dependent variable explained by the model.

Should any component of LUMI involve classification (e.g., categorizing regions by renewable energy suitability levels), the following metrics would apply: accuracy, precision, recall, and F1-score. However, classification metrics are not always appropriate for LUMI because the core forecasting tasks are formulated as regression problems predicting continuous energy output and demand values rather than discrete class labels. Applying classification metrics would require arbitrary binning of continuous predictions, which would lose granularity and potentially misrepresent model performance. Therefore, regression metrics are prioritized, with classification metrics reserved for any explicitly categorical subtasks that may be introduced.

Models are evaluated using train-test splits and time-series cross-validation to ensure that temporal ordering is respected and that models are tested on future periods not seen during training. This prevents data leakage and provides realistic estimates of forecasting accuracy.

Computational Performance Testing

Computational performance testing evaluates the efficiency and resource utilization of LUMI under representative operating conditions. Response time is measured as the elapsed time between a user request and the completion of the system's response, measured at both the API level and frontend level to identify bottlenecks. Memory utilization tracks the amount of RAM consumed by backend services, data processing pipelines, and model inference operations during peak and average load conditions. CPU utilization monitors the percentage of CPU resources consumed during data processing, model training, and API request handling. Processing time measures the time required to complete batch operations such as model training, dataset ingestion, and report generation, distinguished from user-facing response time to assess backend efficiency.

Performance benchmarks are established by measuring each metric under controlled conditions with documented input sizes and request volumes. Baseline measurements are recorded for comparison against optimization efforts in subsequent iterations.

LLM Evaluation Testing

The evaluation of the Google Gemini and Groq API integrations requires specialized testing plans that account for the generative and nondeterministic nature of large language model outputs. A structured benchmark question set is prepared covering a range of query types including factual questions about renewable energy, interpretation of forecast results, recommendation requests, and clarification follow-ups. Each benchmark question has a reference answer prepared by the researchers based on system data and domain knowledge.

The following dimensions are measured: response correctness, where responses are scored on a Likert scale by expert evaluators for factual accuracy; answer relevance, where evaluators assess whether the response addresses the user's intent and provides useful information for renewable energy decision-making; groundedness, verifying the degree to which responses are grounded in the system's data and retrieved knowledge context rather than relying solely on the LLM's parametric knowledge; hallucination rate, measuring the proportion of responses containing fabricated facts, unsupported numerical claims, or contradictory statements; expert validation score, where domain experts rate overall response quality on a standardized rubric encompassing accuracy, completeness, clarity, and usefulness; response latency, measuring the time from query submission to fully rendered response in milliseconds; and token consumption, tracking the number of input and output tokens consumed per query to estimate API usage costs and optimize prompt efficiency.

Traditional classification accuracy is not applicable to LLM evaluation because the AI assistant does not select from a fixed set of labels. Instead, it generates open-ended text where correctness is multidimensional and context-dependent. The evaluation therefore relies on benchmark comparisons, rubric-based expert scoring, and user satisfaction metrics. This approach is consistent with established practices in natural language generation evaluation and acknowledges the inherent subjectivity in assessing text quality.

System Testing

System testing validates the integrated functionality of LUMI as a complete application. Functional testing maps each functional requirement to one or more test cases specifying preconditions, input data, execution steps, and expected outcomes. Integration testing verifies that the frontend, backend, database, and external services interact correctly, with test scenarios including end-to-end workflows such as user login, region selection, data retrieval, forecast generation, and AI assistant query handling. API testing validates backend endpoints for correctness of HTTP methods, response status codes, payload schema conformance, and error handling. User acceptance testing invites potential users and domain experts to perform predefined tasks using the system, recording their ability to complete tasks successfully, the time required, and their subjective satisfaction.

2.7.4. Deployment

During the deployment phase, the researchers conducted a series of testing and evaluation activities to ensure the platform's quality and readiness. This includes system controlled testing, evaluation testing, and usability testing with participants from the target user communities.

The frontend application is deployed as a static site to a cloud hosting platform (e.g., Netlify or Vercel) that provides content delivery network distribution, automatic HTTPS, and continuous deployment from the version control repository. The backend services are deployed to a platform-as-a-service provider (e.g., Render, Railway, or AWS) that supports Python application hosting, environment variable management, and horizontal scaling.

The hosting environment is configured with separate production and staging instances. The staging instance serves as a pre-production environment for final validation before promoting changes to the production instance. Domain configuration, SSL certificates, and DNS records are established to ensure secure and accessible endpoints.

The PostgreSQL database is hosted on Supabase, which provides managed database services, automatic backups, row-level security, and real-time subscriptions. Database migrations are version-controlled and applied through automated deployment pipelines to ensure schema consistency across environments.

External API keys for Google Gemini and Groq are stored as encrypted environment variables and are never committed to version control. API rate limits are monitored, and fallback logic is implemented to switch between providers or degrade gracefully when limits are approached.

The system implements standard security practices including HTTPS enforcement, secure authentication using JSON Web Tokens (JWT), input sanitization, and parameterized database queries to prevent injection attacks. CORS policies are configured to restrict frontend access to authorized domains.

Application logs, error traces, and performance metrics are collected through the hosting platform's monitoring tools. Alert thresholds are configured for high error rates, elevated response times, and memory usage spikes. Regular log reviews are conducted to identify and resolve issues proactively.

A maintenance schedule is established for applying dependency updates, security patches, and model retraining. The model registry tracks model versions and performance history, enabling rollback to previous model versions if updated models exhibit degraded performance. Dataset refresh procedures are documented to ensure that the system's data remains current with new DOE publications and climate records.

