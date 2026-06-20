CHAPTER 9

METHODOLOGY

This chapter presents the methodological framework that guided the development and evaluation of LUMI: Data-Driven Environmental Intelligence System for Renewable Energy Decision Support. It details the purpose of each development phase, the chosen software development life cycle model, the procedures followed to ensure the system was built and validated effectively, and the technical specifications that underpin the system's architecture. The methodology is structured to demonstrate that LUMI was developed through systematic planning, evidence-based design, rigorous implementation, and comprehensive testing.

9.1. Purpose and Description

The purpose of this chapter is to document the complete methodological approach employed in the construction of LUMI. LUMI is a web-based environmental intelligence platform that integrates Philippine energy consumption datasets, environmental and climate data, renewable energy assessment computations, machine learning forecasting models, statistical time-series analysis, and AI-assisted decision support into a unified system. The methodology covers every stage from initial concept formulation through requirements analysis, system design, implementation, testing, evaluation, and deployment.

9.1.1. Conceptual Model of the Study

Figure 1. Conceptual Model of LUMI

The conceptual model of LUMI illustrates the end-to-end flow of information through the system. External data sources, including publications from the Philippine Department of Energy (DOE), climate datasets from NASA POWER, and geographic information from digital elevation models, serve as the system's empirical foundation. These raw data streams pass through a data processing layer where they are cleaned, normalized, and transformed into features suitable for computational analysis. Processed data is then consumed by three parallel analytical pathways: (1) machine learning and statistical forecasting models that project future energy demand; (2) physics-based and empirical renewable energy calculators that estimate solar, wind, and hydropower potential at the municipal level; and (3) a terrain analysis pipeline that derives hydropower suitability metrics from elevation raster data. The outputs of these analytical modules are aggregated in a prediction layer that caches results and manages model versioning. An AI decision support layer, powered by Google Gemini and Groq APIs, processes natural language queries and generates contextual recommendations grounded in system data. Finally, an interactive web-based user interface renders visualizations, forecasts, and AI insights to end users including households, community planners, students, and energy practitioners.

9.1.2. Operational Definition of Terms

Data-Driven Environmental Intelligence refers to the application of data analysis, machine learning, and artificial intelligence techniques to process environmental and energy data in order to generate actionable insights for decision-making. In this study, it encompasses the entire pipeline from raw dataset ingestion to structured recommendation generation.

Renewable Energy Forecasting is the use of predictive models to estimate future energy generation potential from renewable sources such as solar, wind, and hydroelectric power based on historical data, climate conditions, and geographic factors.

Energy Demand Forecasting is the application of statistical and machine learning methods to project future electricity consumption patterns using historical demand data, economic indicators, and temporal trends.

Large Language Model (LLM) is a type of artificial intelligence model trained on extensive text corpora, capable of understanding and generating human-like natural language responses. In this study, LLMs are accessed through the Google Gemini API and Groq API to provide AI-assisted decision support and natural language explanations of energy data.

AutoRegressive Integrated Moving Average (ARIMA) is a statistical time-series forecasting method that models temporal dependencies and trend structures in sequential data. LUMI employs ARIMA as a baseline forecasting approach for national-level energy demand projection.

Retrieval-Augmented Generation (RAG) is a technique that enhances LLM responses by retrieving relevant contextual information from a structured knowledge base before generating answers. LUMI employs RAG to ground AI assistant responses in system data and domain-specific product information.

Vector Database (FAISS) is a data structure optimized for storing and searching high-dimensional vector embeddings. LUMI uses FAISS to enable semantic similarity search over energy-related documents and product descriptions for the AI assistant's knowledge retrieval pipeline.

Ecosim refers to the renewable energy simulation module within LUMI that calculates solar, wind, and hydropower output estimates, generates economic viability indicators, and produces AI-assisted recommendations tailored to a user's municipality and consumption profile.

9.2. Research Design

The study employed a descriptive and developmental research design. The descriptive component involved the systematic collection and analysis of Philippine energy statistics, climate data, and geographic information to characterize the current state of the national energy landscape and the renewable potential of individual municipalities. The developmental component involved the iterative construction of a web-based environmental intelligence system using established software engineering practices.

Data were gathered through document reviews of academic literature, government energy reports, and technical dataset documentation. System observations and testing scripts were used to validate computational correctness and interface usability. Expert consultations informed the design of evaluation rubrics and benchmark questions for the AI assistant component.

To evaluate the platform's forecasting accuracy, computational performance, and overall effectiveness, the researchers applied multiple assessment frameworks. Machine learning model performance was evaluated using standard regression metrics: Mean Absolute Error (MAE), Root Mean Square Error (RMSE), Mean Absolute Percentage Error (MAPE), and the coefficient of determination (R-squared). Computational performance was assessed through response time, memory utilization, and CPU utilization measurements under controlled load conditions. The AI assistant component was evaluated through benchmark question sets, expert validation panels, and rubric-based scoring rather than traditional classification accuracy, given the generative and open-ended nature of large language model outputs.

9.3. Participants or Respondents

The participants of this study represent the primary target user groups of LUMI. These include household decision-makers seeking to evaluate renewable energy options for residential use, community members and local government representatives interested in understanding municipal-level energy potential, students and academic researchers studying Philippine energy systems, and renewable energy professionals who can provide expert validation of the system's technical outputs.

These participants possess varying levels of technical knowledge, ranging from general users with minimal background in energy systems to technically proficient users familiar with data analysis and forecasting concepts. The system was designed to accommodate this diversity through layered visualizations, AI-assisted natural language explanations, and progressively detailed technical outputs.

In addition, energy practitioners, government agency representatives, and academic faculty were included to provide expert insights on data quality, forecasting reliability, usability, and alignment with industry standards and national policy frameworks such as the Philippine Energy Plan. These experts participated in structured evaluation activities including rubric-based scoring of AI assistant responses and review of forecast accuracy against their professional experience.


9.4. Project Development Methodology (Software Development Life Cycle)

Figure 2. Iterative and Incremental Development

For this project, the researchers adopted the Iterative and Incremental Development approach. This model allows the system to be built progressively through repeated cycles (iterations) and in smaller functional portions (increments), enabling continuous improvement based on testing feedback and stakeholder input. Each cycle adds new functional components, allows earlier evaluation of partially completed features, facilitates faster error detection, and provides greater flexibility throughout the development process.

The decision to employ an iterative and incremental approach was grounded in the inherent complexity of LUMI, which integrates machine learning forecasting, environmental data processing, statistical analysis, AI-assisted decision support, renewable energy physics calculations, and interactive visualization within a single coherent platform. Machine learning development is inherently experimental, requiring repeated cycles of model training, hyperparameter adjustment, evaluation against hold-out data, and refinement. The incremental approach allows core functionalities such as data ingestion and preprocessing to be developed and validated independently before integrating more advanced features such as the AI assistant and the Ecosim simulation module.

By using this approach, the system could be refined at every stage, starting from initial planning, proceeding through development and testing, and continuing through ongoing revisions. This ensured alignment with user needs, project goals, and technical feasibility throughout the project lifecycle. The following phases describe the structured activities conducted within each iteration of the development cycle.

Phase 1: Planning

In the initial planning phase, the researchers gathered system requirements and studied existing environmental intelligence platforms, renewable energy decision support tools, and energy forecasting systems to identify key features, design patterns, and common limitations. The team reviewed publicly available energy datasets from the Philippine Department of Energy and climate data from the NASA POWER project to assess their relevance, completeness, temporal coverage, and accessibility. A modular system architecture was planned to allow isolated development of each subsystem and to ensure easier integration during later phases.

The programming team reviewed the programming languages, frameworks, and tools required for implementation. Python was selected for backend development, machine learning, and data processing due to its extensive ecosystem of scientific computing libraries including pandas, NumPy, scikit-learn, statsmodels, and PyTorch. React with Tailwind CSS was chosen for the frontend to ensure component reusability, responsive design, and efficient state management. Supabase was selected for managed PostgreSQL database services due to its real-time capabilities, row-level security, and seamless integration with web applications. Google Gemini and Groq APIs were identified as the primary large language model providers for the AI assistant functionality.

The documentation team collected academic references on renewable energy forecasting, environmental intelligence systems, machine learning methodologies, statistical time-series analysis, and micro-hydropower engineering. Initial test plans were drafted and reviewed with the development team for alignment with functional requirements. Roles were assigned based on individual strengths and expertise. The project manager ensured that all planning tasks progressed on time and remained coordinated across the team.

Phase 2: Requirements Analysis

During the requirements phase, the researchers conducted an in-depth investigation into the key functions and scope expected of an environmental intelligence system for renewable energy decision support. This process involved analyzing existing platforms, reviewing user needs documented in preliminary surveys, and identifying essential features that define an effective and data-driven decision support experience.

The team documented functional requirements using formal "shall" statements to ensure clarity, testability, and traceability. These requirements covered user interaction and navigation, renewable energy potential forecasting for solar wind and hydro sources, energy demand forecasting at the national level, data ingestion and preprocessing from government and scientific sources, machine learning prediction modules, statistical forecasting modules using ARIMA, AI assistant integration for natural language queries, Google Gemini and Groq API interaction, interactive data visualization and dashboard design, structured reports and recommendations, model results display with confidence intervals, persistent data storage, and web-based deployment accessibility.

Throughout the development process, the team continuously gathered and documented new requirements derived from user feedback, expert consultation, and ongoing project developments. Each new input was carefully evaluated and integrated into the planning and design phases to ensure the system remained responsive, adaptive, and aligned with the evolving goals of the project.

Phase 3: System Design

To design the platform effectively, the researchers grounded their architectural decisions in document reviews and an analysis of existing environmental intelligence systems. These efforts provided a clearer understanding of what target users expect from a modern renewable energy decision support environment, and what the literature indicates are the most effective strategies for presenting energy data and forecasts to audiences with varying technical backgrounds.

Given that the target users include households, community members, students, and government institutions, the platform was developed with the assumption that users possess varying levels of technical expertise. The system was designed to start with accessible data visualizations and guided insights, transitioning to more detailed forecasts and AI-assisted explanations for users who require deeper analysis.

The design incorporates a layered architecture comprising data sources, data processing, machine learning models, renewable energy calculation engines, a prediction and caching layer, an AI decision support layer, and an interactive user interface. This modular structure ensures that changes at any level, such as replacing a machine learning model, updating a climate data source, or refining the AI assistant prompt logic, can be implemented without destabilizing the entire system. Database schemas were designed to store energy datasets, environmental data, model outputs, terrain metrics, user interactions, and AI responses. User interface mockups were created early in the design phase to establish layout conventions and reduce design-related workload during later development.

Phase 4: Development / Implementation

During the implementation phase, the system was developed incrementally based on the finalized design and modular structure. The programmers focused on building core functionalities for each module, including data ingestion pipelines for DOE statistics and NASA POWER climate data, preprocessing utilities for missing value imputation and feature engineering, machine learning forecasting models using ARIMA and gradient boosting approaches, statistical time-series analysis, backend REST APIs using FastAPI, frontend dashboard components using React, the Ecosim renewable energy simulation module, and AI assistant integration using Google Gemini and Groq.

Frontend components were built using React, Tailwind CSS, and Vite, while backend logic was implemented in Python using FastAPI with Uvicorn as the ASGI server. Supabase was utilized for structured data storage, geographic dimension tables, and user management. Machine learning models were trained using scikit-learn, statsmodels, and PyTorch on Philippine energy and environmental datasets. The Google Gemini and Groq APIs were integrated to provide natural language query processing and contextual decision support.

As each module was implemented, the team conducted continuous testing to ensure stability and functionality. Unit testing and integration testing were performed by the researchers using multiple devices to assess compatibility and performance. Identified issues were immediately documented in the issue tracker and resolved before proceeding to the next cycle of development.

Phase 5: Testing

The testing phase involved verifying the functionality, stability, and accuracy of the system. The researchers conducted multiple levels of testing, including unit testing for individual functions and components, integration testing for frontend-backend communication, system testing for end-to-end workflows, and machine learning model evaluation against hold-out test data. These tests ensured that each module worked as intended and that the platform was responsive, accessible, and free of critical errors.

Machine learning models were evaluated using held-out test datasets and statistical metrics including MAE, MSE, RMSE, MAPE, and R-squared. API endpoints were tested for correctness, response time, and error handling under both normal and edge-case conditions. The AI assistant was evaluated through benchmark question sets and expert validation. The Ecosim simulation module was validated against known physical relationships, such as the cubic relationship between wind speed and power output, and the linear relationship between hydraulic head and hydropower potential. Issues found during testing were documented and resolved before proceeding to the evaluation phase.

Phase 6: Evaluation

Following the completion of testing, the system underwent structured evaluation to measure its overall quality and effectiveness. Machine learning prediction accuracy was evaluated using appropriate statistical metrics against test data spanning 2021 to 2024. Computational performance was assessed through response time, memory utilization, and CPU utilization measurements under representative operating conditions.

The AI assistant's responses were evaluated on dimensions including factual correctness, relevance to the user's query, groundedness in system data, hallucination rate, expert validation score, response latency, and token consumption. This evaluation relied on benchmark question sets and human expert review rather than traditional classification accuracy, which is not applicable to generative text tasks. An acceptability evaluation was conducted with participants from the target user communities to gather feedback on the system's visual design, clarity, learnability, and user engagement.

Phase 7: Deployment

In the deployment phase, the system was launched in a controlled environment for demonstration and testing purposes. The frontend application was deployed as a static site to a cloud hosting platform that provides content delivery network distribution, automatic HTTPS, and continuous deployment from the version control repository. The backend services were deployed to a platform-as-a-service provider supporting Python application hosting.

The PostgreSQL database was hosted on Supabase, which provides managed database services, automatic backups, row-level security, and real-time subscriptions. External API keys for Google Gemini and Groq were configured as encrypted environment variables and were never committed to version control. Security measures including HTTPS enforcement, JWT authentication, input sanitization, and parameterized database queries were implemented to prevent injection attacks and unauthorized access.

As part of the deployment process, researchers conducted a pilot run with selected participants from the target user communities. Participants were invited to interact with the platform, explore key modules including the EnergyHub dashboard, Ecosim simulation, and AI assistant, and provide feedback on usability and functionality. Observations from this pilot deployment were recorded to identify final areas for refinement before the system was considered ready for broader use.


9.5. Requirements Specifications: Tools, Technologies, or Platforms Used

This section outlines the key software, hardware, programming languages, frameworks, and platforms needed to develop and run LUMI. It provides a clear view of the technical environment, helping the development team and stakeholders remain aligned on the tools and resources that support the system's overall functionality.

9.5.1. Functional Requirements

The system shall provide a user-friendly web interface that allows users to navigate between modules including the climate and energy dashboard, forecasting tools, Ecosim simulation, recommendation engine, and AI assistant.

The system shall support user authentication and session management to ensure secure access to personalized features and saved preferences.

The system shall allow users to select Philippine regions, provinces, and municipalities to receive localized energy and environmental insights.

The system shall implement machine learning models capable of forecasting renewable energy generation trends and national energy demand based on historical and environmental data.

The system shall display forecasted energy metrics with appropriate confidence intervals and temporal granularity.

The system shall implement statistical time-series forecasting models, specifically ARIMA(1,1,1), to predict future energy demand trends based on historical consumption patterns.

The system shall present energy demand forecasts through interactive visualizations that allow users to explore projections across different time horizons.

The system shall ingest publicly available energy datasets from the Department of Energy (DOE) and environmental datasets from the NASA POWER project.

The system shall support automated data retrieval from external APIs and manual import of structured datasets in standard formats such as CSV and JSON.

The system shall implement data preprocessing pipelines that handle missing values through forward-fill and backward-fill imputation, outlier detection, data normalization, and feature engineering prior to model training.

The system shall validate incoming data for format consistency, completeness, and integrity before processing.

The system shall implement supervised learning algorithms for regression tasks related to energy output and demand prediction.

The system shall provide functionality for model training, hyperparameter tuning, time-series cross-validation, and performance evaluation using MAE, RMSE, MAPE, and R-squared.

The system shall store trained model artifacts and metadata in a versioned manner through the ml_model_registry table to support reproducibility and comparison.

The system shall implement statistical forecasting techniques such as ARIMA and related time-series methods for baseline comparison and trend analysis.

The system shall generate forecast outputs with diagnostic plots including residual analysis and autocorrelation functions.

The system shall integrate an AI assistant capable of interpreting user queries related to renewable energy, climate data, and energy demand.

The system shall process natural language inputs and generate informative, contextually relevant responses based on system data and retrieved knowledge.

The system shall interface with the Google Gemini API and Groq API to leverage large language model capabilities for decision support and recommendation generation.

The system shall implement prompt engineering strategies, including system context injection and retrieval-augmented generation, to ensure that API inputs are structured for optimal response quality.

The system shall handle API errors, rate limits, and fallback mechanisms to maintain service availability.

The system shall provide interactive data visualizations including charts, graphs, and choropleth maps to represent climate patterns, energy trends, and forecast results.

The system shall implement a responsive dashboard layout that adapts to various screen sizes and devices.

The system shall generate structured reports summarizing energy forecasts, renewable energy potential assessments, and recommendation rationales.

The system shall present recommendation outputs in a clear, actionable format suitable for non-technical users.

The system shall display model performance metrics, prediction results, and comparative analyses in an interpretable format.

The system shall provide model explanation features that highlight key factors influencing predictions.

The system shall persistently store energy datasets, environmental data, model outputs, user interactions, and AI assistant responses in a structured PostgreSQL database.

The system shall implement data access controls through Supabase Row Level Security to ensure the security and privacy of stored information.

The system shall be deployable as a web application accessible through standard internet browsers without requiring specialized client software.

The system shall provide consistent performance and availability within the constraints of the chosen deployment platform.

9.5.2. Software Requirements

Table 1. Software Requirements Table

| Category | Tool / Technology | Purpose | Usage in LUMI |
|----------|-----------------|---------|---------------|
| Development Environment | Visual Studio Code | Integrated development environment for writing, debugging, and managing code across the entire project. | Primary IDE for frontend, backend, and scripting development. |
| Programming Languages | Python 3.12+ | Backend development, machine learning model implementation, data processing, and API services. | Used for FastAPI backend, ML pipelines, data extraction, and forecasting notebooks. |
| Programming Languages | JavaScript (ES6+) | Frontend application logic, component interactivity, and client-side data handling. | Used for React-based user interface development. |
| Programming Languages | HTML5 / CSS3 | Web page structure and styling for the frontend application. | Used within the React framework for UI rendering and Tailwind CSS styling. |
| Machine Learning Libraries | scikit-learn | General-purpose machine learning algorithms including regression, preprocessing, and model evaluation utilities. | Used for feature engineering, model training, and baseline prediction tasks. |
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

9.5.3. Hardware Requirements

Table 2. Hardware Requirements Table

| Category | Minimum Requirement | Recommended Requirement | Development Requirement |
|----------|---------------------|------------------------|------------------------|
| Processor | Intel Core i3 or AMD Ryzen 3 (quad-core, 2.0 GHz) | Intel Core i5 or AMD Ryzen 5 (hexa-core, 2.5 GHz) | Intel Core i7 or AMD Ryzen 7 (octa-core, 2.8 GHz) |
| Memory | 8 GB DDR4 | 16 GB DDR4 | 32 GB DDR4 |
| Hard Disk | 256 GB SSD | 512 GB SSD | 1 TB SSD |
| GPU | Integrated graphics (sufficient for web rendering) | Dedicated GPU with 4 GB VRAM (for accelerated ML training) | NVIDIA GPU with CUDA support, 8 GB+ VRAM (for deep learning experimentation) |
| Internet Connection | Stable broadband connection (5 Mbps) | High-speed broadband connection (25 Mbps) | High-speed broadband connection (50 Mbps or higher) |
| Operating System | Windows 10, macOS 11, or Linux (Ubuntu 20.04) | Windows 11, macOS 13, or Linux (Ubuntu 22.04) | Windows 11 Pro, macOS 14, or Linux (Ubuntu 22.04) |

The development requirements are specified to accommodate the computational demands of training machine learning models, processing large environmental datasets, running the terrain analysis pipeline on elevation rasters, running multiple services simultaneously (frontend, backend, database), and executing Jupyter notebooks for exploratory data analysis. For end users accessing the deployed web application, the minimum requirements are sufficient as the majority of computation occurs on the server side. The GPU requirement is primarily relevant for development and experimentation with deep learning models; the deployed system does not require client-side GPU capabilities.


9.6. Data Gathering Procedures

9.6.3. Document Reviews

To support the development and contextual relevance of the platform, the researchers conducted a systematic review of academic literature, institutional materials, government reports, and technical dataset documentation related to renewable energy, environmental intelligence, energy forecasting, and machine learning applications in the energy domain. This review covered publications from 2021 to 2025, with particular attention given to studies conducted in Southeast Asian contexts and island nations with climates and grid structures comparable to the Philippines.

Peer-reviewed journal articles and conference papers were reviewed to understand the state of the art in renewable energy forecasting, environmental intelligence systems, and machine learning applications in the energy domain. These sources provided insights into algorithm selection, feature engineering strategies, and evaluation methodologies that were adapted for the Philippine context. Particular attention was given to the performance of ARIMA models and gradient boosting approaches for national-level energy demand forecasting in developing economies.

Existing studies on energy demand forecasting and renewable energy output prediction were examined to identify appropriate statistical and machine learning techniques. Studies by Ngwakwe (2025), Huda et al. (2024), and Asadi et al. (2023) informed the selection of evaluation metrics such as MAPE and payback period for economic assessment. Particular attention was given to studies conducted in Southeast Asian contexts and island nations with climates and grid structures comparable to the Philippines.

Literature on renewable energy adoption, site feasibility analysis, and multi-criteria decision-making was reviewed to inform the design of the Ecosim recommendation engine. Studies examining public perception, economic factors, and technical criteria for renewable energy selection provided the basis for the weighted linear combination scoring approach used in the _calculate_option_summary function.

Textbooks and methodological papers on supervised learning, time-series analysis, deep learning, and model evaluation were consulted to ensure rigorous application of machine learning practices. These references guided the selection of appropriate metrics, validation strategies including temporal train-test splits, and experimental designs for model testing.

Official publications from the Philippine Department of Energy (DOE), the National Grid Corporation of the Philippines, and the Philippine Atmospheric, Geophysical and Astronomical Services Administration (PAGASA) were reviewed to identify available datasets, understand national energy statistics, and align the system's scope with official energy planning frameworks. The DOE 2019-2021 National Grid Emission Factor of 0.6835 kg CO2 per kWh was identified as the authoritative value for carbon displacement calculations in the Ecosim module.

Technical documentation accompanying NASA POWER climate datasets, Shuttle Radar Topography Mission (SRTM) elevation models, and geographic information system (GIS) data was reviewed to ensure correct interpretation and processing of environmental variables. This documentation was essential for the accurate integration of meteorological and topographic data into prediction models and terrain analysis pipelines.

The insights gathered from document reviews directly informed the system architecture, algorithm selection, feature definitions, economic formulas, and evaluation criteria employed in LUMI. They also provided the evidentiary basis for the significance of the study and the design choices documented in this methodology.

9.6.4. Observation

Observation was used as a method to analyze user interaction with the platform during the testing phase. Selected participants were observed as they navigated the system's features, explored the dashboard, interpreted forecast visualizations, interacted with the Ecosim simulation module, and conversed with the AI assistant. The researchers took note of usability issues, confusion points, and behavioral patterns.

During system testing, researchers observed the system's behavior under various input conditions. This included monitoring the accuracy of data visualizations, the correctness of prediction outputs, the stability of API integrations, the responsiveness of the Ecosim calculation pipeline, and the consistency of AI assistant responses. Observations were documented in structured logs to facilitate defect reporting and iterative improvement.

During user interaction evaluation, potential users were invited to interact with the system while researchers observed their navigation patterns, task completion efficiency, and areas of confusion. The researchers recorded observations regarding the intuitiveness of the dashboard layout, the clarity of visualization labels, and the ease of accessing forecasting and recommendation features.

During dashboard usage observation, researchers observed how users interpreted energy trend visualizations, forecast charts, and geographic choropleth maps. Particular attention was given to whether users could correctly extract actionable insights from the presented data and whether the visual encoding of information (colors, scales, legends) supported accurate understanding.

During Ecosim interaction observation, researchers monitored how users entered household parameters, interpreted renewable energy estimates, and understood economic indicators such as payback period and carbon reduction. Special attention was given to whether the distinction between estimated generation and usable generation (capped at consumption) was clearly communicated.

During AI assistant interaction observation, the quality of AI assistant interactions was assessed through observation of user query patterns and the generated responses. Researchers observed whether the AI assistant correctly understood domain-specific questions, provided relevant and factually grounded answers, and maintained coherence across multi-turn conversations.

The following aspects were systematically observed and documented: usability issues, including identification of interface elements that caused confusion, navigation delays, or errors in user input; response quality, encompassing assessment of AI assistant answers for factual correctness, relevance to the query, and completeness of information; system behavior, monitoring unexpected system states, error messages, performance degradation, or inconsistent outputs; prediction presentation, evaluating whether forecast results and model outputs were presented in a manner that supported user understanding and decision-making; and user difficulties, documenting tasks that users struggled to complete, features that were difficult to locate, and terminology that required clarification.

Observation records were compiled and analyzed to generate actionable recommendations for interface refinements, workflow improvements, and additional user guidance features.

9.6.5. Testing Scripts / Code

To ensure system reliability, accuracy, and functionality, the researchers conducted a series of internal tests using pre-written scripts and manual walkthroughs. The testing process included debugging, validating logic flows, and checking system components such as data processing pipelines, machine learning model inference, API responses, Ecosim calculation functions, terrain analysis outputs, and interactive modules. Functional testing and unit testing were applied to identify errors and verify expected outputs. The test results guided refinements and adjustments to the platform's backend and user interface before pilot deployment. All code-related changes were documented and version-controlled for traceability.

The following categories of testing scripts were created. Machine learning model evaluation scripts were developed to automate the evaluation of forecasting models using standard statistical metrics. These scripts loaded trained models, applied them to held-out test datasets, and computed performance indicators such as MAE, MSE, RMSE, MAPE, and R-squared. The scripts also generated diagnostic visualizations including residual plots and prediction versus actual value scatter plots.

API testing scripts were used to validate backend API endpoints. Automated test scripts verified correct HTTP response codes, response payload structure, data type consistency, and error handling behavior. These scripts tested authentication flows, data retrieval endpoints, EnergyHub forecast serving, Ecosim calculation handling, and AI assistant query processing under both normal and edge-case conditions.

Backend testing scripts included unit test scripts written to verify the correctness of individual functions and classes in the backend codebase. Integration test scripts validated the interactions between database layers, business logic modules, and external service clients. The test suite for renewable energy calculations covered solar temperature factor computation, dust loss adjustment, performance ratio aggregation, wind power calculation including Betz limit validation, hydropower flow estimation, and hydraulic power conversion.

Data processing validation scripts were created to validate the integrity and correctness of data preprocessing pipelines. These scripts checked for data type conformance, missing value handling using forward-fill and backward-fill strategies, outlier detection accuracy, and the correctness of feature engineering transformations such as lag feature creation and trend variable construction. They also verified that processed datasets maintained referential integrity and statistical consistency with source data.

System functionality testing scripts simulated complete user workflows, from region selection and data visualization to forecast generation, Ecosim simulation execution, and recommendation retrieval. These scripts validated that the integrated system produced coherent results across multiple modules and that user actions triggered the correct sequence of backend processes.

Examples of validation checks performed by testing scripts include input validation, verifying that the system rejects invalid or malformed inputs (e.g., out-of-range dates, unsupported municipalities, negative electricity bills, empty query strings) with appropriate error messages; prediction accuracy checking, comparing model outputs against known test values to ensure that predictions fall within expected ranges and that model drift is detected; physics validation, confirming that wind power outputs scale with the cube of wind speed and that hydropower outputs scale linearly with hydraulic head; response time measurement, recording the latency of API calls, model inference operations, and AI assistant response generation to ensure compliance with performance requirements; memory utilization monitoring, tracking memory consumption during data processing, model training, terrain raster analysis, and concurrent user request handling to identify potential inefficiencies or memory leaks; and error handling, deliberately triggering error conditions (e.g., unavailable external APIs, missing database records, malformed data) to verify that the system responds gracefully and provides informative feedback.


9.7. System Development Procedures

9.7.1. Planning

Project Schedule: Gantt Chart

Figure 3. Gantt Chart of LUMI - Phase 1

Figure 4. Gantt Chart of LUMI - Phase 2

Feasibility Study

Development and Operational Cost
The projected cost of the system remains highly practical due to the reliance on free-tier services for hosting, server maintenance, and frameworks during the initial development and pilot testing phases. These free plans are sufficient for the initial deployment and evaluation of the platform. In the event of scaling or exceeding usage limits, potential expenses may include Supabase for managed PostgreSQL database services, Netlify or Vercel for frontend static site hosting, and Render or Railway for backend Python application hosting. Even with these possible upgrades, the total operational costs remain minimal compared to typical enterprise-level environmental intelligence platforms, ensuring financial manageability and sustainability for an academic research project.

Project Planning
The researchers developed a comprehensive project plan that outlined the major milestones, deliverables, and evaluation criteria for the study. The plan allocated time for literature review, dataset acquisition, prototype development, model training, terrain pipeline execution, system integration, testing, and documentation. Risk factors such as data availability from government sources, API reliability for climate data and LLM services, computational resource constraints for terrain raster processing, and model accuracy limitations were identified and mitigation strategies were formulated for each.

Requirement Gathering
Functional and non-functional requirements were gathered through review of existing environmental intelligence systems, analysis of Philippine energy sector needs documented in DOE planning publications, and consideration of the target user population's technical diversity. Requirements were prioritized based on their contribution to the study's objectives and their feasibility within the project timeline. Requirements were documented as formal "shall" statements to ensure testability and traceability.

Dataset Identification
Publicly available datasets from the Philippine Department of Energy, NASA POWER climate API, and Shuttle Radar Topography Mission (SRTM) elevation data were identified and catalogued. The researchers evaluated datasets for relevance, completeness, temporal coverage, spatial resolution, and licensing terms. Data acquisition procedures including REST API access, bulk CSV download, and extraction from published reports were established. The Philippine geographic hierarchy (regions, provinces, municipalities, barangays) was identified as the spatial framework for localizing climate and energy insights.

Technology Selection
The technology stack was selected based on the requirements for scalability, maintainability, performance, and alignment with the researchers' technical competencies. Python was selected for backend and machine learning development due to its extensive ecosystem of scientific computing libraries. React with Tailwind CSS was selected for frontend development to ensure component reusability and responsive design. Supabase was selected for database services to leverage managed PostgreSQL with real-time capabilities and row-level security. Google Gemini and Groq APIs were selected for AI assistant functionality based on their performance characteristics, integration support, and complementary inference speeds.

Team and Task Organization
Development responsibilities were distributed among team members according to expertise areas including frontend development, backend API development, machine learning engineering, data processing and terrain analysis, and technical documentation. Regular coordination meetings were scheduled to synchronize progress, resolve blockers, and align on design decisions. Version control through Git and GitHub was used to manage concurrent development and track changes.

9.7.2. Software Design

9.7.2.1. Conceptual Design

Figure 5. Conceptual Design of LUMI

LUMI is designed as a web-based environmental intelligence platform that integrates data-driven forecasting, physics-based renewable energy calculations, AI-assisted recommendations, and interactive visualization. The system follows a layered architecture that separates concerns among data acquisition, processing, modeling, intelligence, and presentation layers. This separation ensures that modifications to one layer, such as updating a climate data source or replacing a forecasting algorithm, do not destabilize the entire system.

The data flow through the system follows a pipeline structure. Data Sources form the foundation of LUMI, integrating multiple data streams including Philippine Department of Energy statistical publications, NASA POWER climate and meteorological datasets, SRTM geographic and terrain elevation data, and scraped product information for renewable energy equipment. External APIs provide real-time or periodic data updates where available.

Data Processing receives raw data from various sources through preprocessing pipelines that normalize formats, resolve inconsistencies, handle missing values through forward-fill and backward-fill imputation, and engineer features suitable for machine learning. This layer also includes extraction, transformation, and loading procedures for structured storage in the PostgreSQL database.

Machine Learning Models receive processed data and perform forecasting and prediction tasks. This layer includes ARIMA time-series models for national energy demand forecasting, linear trend regression for baseline comparison, and gradient boosting models for comparative evaluation. Model outputs are persisted in CSV artifacts and loaded at runtime by the prediction service.

Renewable Energy Calculation Engines receive municipal climate averages and terrain metrics to compute solar, wind, and hydropower potential using physics-based and empirical formulas. The solar calculator adjusts for temperature, dust, and humidity losses. The wind calculator applies the fundamental wind power equation with validated power coefficients. The hydropower calculator estimates design flow from terrain slope and rainfall, then computes electrical output from hydraulic head and turbine efficiency.

The Prediction Layer aggregates, formats, and enriches model outputs with metadata. This layer manages model versioning through the ml_model_registry table, result caching in the forecast_cache table, and the assembly of historical and forecasted data for charting.

The AI Decision Support Layer integrates large language model capabilities through the Google Gemini and Groq APIs. It processes natural language queries, retrieves relevant system data and knowledge context using FAISS vector search, and generates interpretive responses, recommendations, and scenario analyses. Chart-specific insights are cached in the chart_ai_insights table to reduce latency and API costs.

The User Interface delivers the system's capabilities through an interactive web-based dashboard. Users can visualize national energy trends, explore municipal-level renewable potential on choropleth maps, run the Ecosim simulation for personalized recommendations, and interact with the AI assistant through a conversational interface. The interface is built responsively to accommodate desktop and mobile devices.

This layered architecture ensures that changes at any level can be implemented without destabilizing the entire system, supporting maintainability and extensibility.

9.7.2.2. Technical Design

9.7.2.2.1. Context Data Flow Diagram

Figure 6. Context Data Flow Diagram of LUMI

This figure presents the Context Data Flow Diagram of LUMI, representing an early-stage prototype of the system. It provides a high-level overview of how the system interacts with external entities, namely the users (seeking renewable energy insights and energy data) and the admin (researchers managing the system and updating datasets).

9.7.2.2.2. Top-Down Data Flow Diagram

Figure 7. Top-Down Data Flow Diagram

9.7.2.2.3. Logical Data Flow Diagram

Figure 8. EnergyHub Logical DFD

Figure 9. Ecosim Logical DFD

Figure 10. AI Assistant Logical DFD

Figure 11. Data Ingestion Logical DFD

9.7.2.2.4. Physical Data Flow Diagram

Figure 12. EnergyHub Physical DFD

Figure 13. Ecosim Physical DFD

Figure 14. AI Assistant Physical DFD

Figure 15. Data Ingestion Physical DFD

9.7.2.2.5. Entity Relationship Diagram

Figure 16. Entity Relationship Diagram of LUMI

The Entity Relationship Diagram illustrates the logical structure of the LUMI database and the relationships among its constituent tables. The database schema is organized around geographic dimensions, climate data, energy statistics, terrain metrics, machine learning model registry, forecast caching, AI insights, and administrative metadata.

The geographic hierarchy is modeled through four normalized tables: regions, provinces, municipalities, and barangays. The regions table serves as the top-level administrative division, containing region identifiers and geographic coordinates. Each region is associated with one or more provinces through a one-to-many relationship via region_id. The provinces table stores province identifiers, names, and coordinates, and links to regions. Each province is associated with one or more municipalities through a one-to-many relationship via province_id. The municipalities table stores municipality identifiers, names, and coordinates, and links to provinces. Each municipality is associated with one or more barangays through a one-to-many relationship via municipality_id. The barangays table stores barangay identifiers, names, and coordinates. This hierarchical structure enables localized analysis and drill-down from national to barangay-level insights.

The municipality_climate_monthly table stores monthly historical climate data for each municipality, sourced from NASA POWER. It is linked to municipalities through municipality_id. Its composite primary key consists of municipality_id, year, and month, ensuring that each municipality has at most one climate record per month. This table contains temperature, humidity, precipitation, wind speed, solar irradiance, cloud cover, surface pressure, and air density measurements.

The national_energy_annual table stores Philippine national energy statistics extracted from DOE publications. Its primary key is year. It contains generation and consumption metrics by source and grid, enabling time-series analysis and forecasting.

The hydropower_suitability table stores terrain-derived hydropower metrics for each municipality. It is linked to municipalities and provinces through foreign keys. It contains elevation statistics, slope measurements, hydraulic head estimates, runoff potential, gravity flow potential, and a composite hydro suitability score.

The ml_model_registry table tracks trained forecasting models, with a composite unique index on target_variable and is_active to ensure only one active model per target. The forecast_cache table stores pre-computed forecasts and links to ml_model_registry through model_id. The chart_ai_insights table caches AI-generated chart explanations.

The user authentication and personalization layer is modeled through the `profiles`, `user_roles`, `saved_simulations`, `saved_locations`, `chat_sessions`, `chat_messages`, `user_usage_limits`, and `admin_audit_log` tables. The `profiles` table extends Supabase Auth user metadata with editable fields including full name, organization, location, and preferred municipality. The `user_roles` table stores a single role per user from the `app_role` enum (`user`, `admin`, `dev`), enabling role-based access control. The `saved_simulations` and `saved_locations` tables persist user-specific EcoSim results and municipality bookmarks, both foreign-keyed to `auth.users`. The `chat_sessions` and `chat_messages` tables store conversational history for the RAG-powered AI assistant, with `chat_messages` referencing `chat_sessions` through a foreign key. The `user_usage_limits` table tracks monthly consumption against plan limits. The `admin_audit_log` table records all privileged administrative actions for accountability.

A regional_lookup view joins all geographic hierarchy tables to provide a unified query interface for frontend location selection.


9.7.2.2.6. Data Dictionary

The data dictionary documents all tables, views, columns, data types, constraints, and relationships defined in the LUMI PostgreSQL database schema. Every field described below is derived from the actual schema definition used in production.

Table 3. regions

Purpose: Stores top-level administrative regions of the Philippines.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| region_id | integer | Unique identifier for each region. | PRIMARY KEY |
| name | text | Official region name. | NOT NULL |
| lat | double precision | Region centroid latitude. | Nullable |
| lon | double precision | Region centroid longitude. | Nullable |

Relationships: One-to-many with provinces via region_id.

Table 4. provinces

Purpose: Stores provinces belonging to regions.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| province_id | integer | Unique identifier for each province. | PRIMARY KEY |
| region_id | integer | Parent region identifier. | NOT NULL, FOREIGN KEY references regions(region_id) ON UPDATE CASCADE ON DELETE RESTRICT |
| name | text | Official province name. | NOT NULL |
| lat | double precision | Province centroid latitude. | Nullable |
| lon | double precision | Province centroid longitude. | Nullable |

Relationships: Many-to-one with regions. One-to-many with municipalities via province_id.

Table 5. municipalities

Purpose: Stores municipalities belonging to provinces.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| municipality_id | integer | Unique identifier for each municipality. | PRIMARY KEY |
| province_id | integer | Parent province identifier. | NOT NULL, FOREIGN KEY references provinces(province_id) ON UPDATE CASCADE ON DELETE RESTRICT |
| name | text | Official municipality name. | NOT NULL |
| lat | double precision | Municipality centroid latitude. | Nullable |
| lon | double precision | Municipality centroid longitude. | Nullable |

Relationships: Many-to-one with provinces. One-to-many with barangays via municipality_id. One-to-many with municipality_climate_monthly via municipality_id. One-to-one with hydropower_suitability via municipality_id.

Table 6. barangays

Purpose: Stores barangays belonging to municipalities.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| barangay_id | integer | Unique identifier for each barangay. | PRIMARY KEY |
| municipality_id | integer | Parent municipality identifier. | NOT NULL, FOREIGN KEY references municipalities(municipality_id) ON UPDATE CASCADE ON DELETE RESTRICT |
| name | text | Official barangay name. | NOT NULL |
| lat | double precision | Barangay centroid latitude. | Nullable |
| lon | double precision | Barangay centroid longitude. | Nullable |

Relationships: Many-to-one with municipalities. Indexed on municipality_id for fast lookup.

Table 7. municipality_climate_monthly

Purpose: Stores monthly historical climate data by municipality from NASA POWER. Used as input for renewable energy calculations and environmental scoring.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| municipality_id | integer | Parent municipality identifier. | NOT NULL, FOREIGN KEY references municipalities(municipality_id) ON UPDATE CASCADE ON DELETE RESTRICT |
| year | smallint | Year of observation. | NOT NULL, CHECK (year >= 2010) |
| month | smallint | Month of observation (1-12). | NOT NULL, CHECK (month >= 1 AND month <= 12) |
| t2m | double precision | Mean air temperature at 2 meters (Celsius). | Nullable |
| t2m_max | double precision | Maximum air temperature at 2 meters (Celsius). | Nullable |
| t2m_min | double precision | Minimum air temperature at 2 meters (Celsius). | Nullable |
| rh2m | double precision | Relative humidity at 2 meters (percent). | Nullable |
| prectotcorr | double precision | Precipitation corrected (mm/day). | Nullable |
| ws10m | double precision | Wind speed at 10 meters (m/s). | Nullable |
| allsky_sfc_sw_dwn | double precision | All-sky surface shortwave downward irradiance (kWh/m^2/day). | Nullable |
| source | text | Data source identifier; defaults to 'NASA POWER'. | NOT NULL, DEFAULT 'NASA POWER' |
| created_at | timestamp with time zone | Record creation timestamp. | NOT NULL, DEFAULT now() |
| cloud_amt | double precision | Cloud amount (percent). | Nullable |
| surface_pressure | double precision | Surface pressure (kPa). | Nullable |
| elevation | double precision | Elevation factor for hydropower analysis. | Nullable |
| rhoa | double precision | Surface air density (kg/m^3). | Nullable |

Relationships: Many-to-one with municipalities. Composite PRIMARY KEY on (municipality_id, year, month). Indexed on municipality_id, year, month, and combinations thereof for time-series queries.

Table 8. national_energy_annual

Purpose: Stores Philippine national energy statistics extracted from DOE publications. Used as target variables for ML forecasting and as reference data for the EnergyHub dashboard.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| year | smallint | Year of statistics. | PRIMARY KEY, CHECK (year >= 2000 AND year <= 2100) |
| total_consumption_gwh | numeric(12,2) | Total electricity consumption including system losses and utilities own use. | Nullable, CHECK (total_consumption_gwh >= 0) |
| residential_consumption_gwh | numeric(12,2) | Residential sector consumption. | Nullable |
| commercial_consumption_gwh | numeric(12,2) | Commercial sector consumption. | Nullable |
| industrial_consumption_gwh | numeric(12,2) | Industrial sector consumption. | Nullable |
| others_consumption_gwh | numeric(12,2) | Other sector consumption. | Nullable |
| electricity_sales_gwh | numeric(12,2) | Total electricity sales. | Nullable |
| utilities_own_use_gwh | numeric(12,2) | Utilities' own use. | Nullable |
| system_losses_gwh | numeric(12,2) | System losses. | Nullable |
| luzon_peak_demand_mw | numeric(12,2) | Luzon grid peak demand. | Nullable |
| visayas_peak_demand_mw | numeric(12,2) | Visayas grid peak demand. | Nullable |
| mindanao_peak_demand_mw | numeric(12,2) | Mindanao grid peak demand. | Nullable |
| total_peak_demand_mw | numeric(12,2) | Total non-coincident peak demand across all grids. | Nullable, CHECK (total_peak_demand_mw >= 0) |
| luzon_generation_gwh | numeric(12,2) | Luzon grid generation. | Nullable |
| visayas_generation_gwh | numeric(12,2) | Visayas grid generation. | Nullable |
| mindanao_generation_gwh | numeric(12,2) | Mindanao grid generation. | Nullable |
| coal_generation_gwh | numeric(12,2) | Coal-fired generation. | Nullable |
| oil_based_generation_gwh | numeric(12,2) | Oil-based generation. | Nullable |
| natural_gas_generation_gwh | numeric(12,2) | Natural gas generation. | Nullable |
| renewable_generation_gwh | numeric(12,2) | Combined renewable generation (geothermal + hydro + biomass + solar + wind). | Nullable |
| geothermal_generation_gwh | numeric(12,2) | Geothermal generation. | Nullable |
| hydro_generation_gwh | numeric(12,2) | Hydroelectric generation. | Nullable |
| biomass_generation_gwh | numeric(12,2) | Biomass generation. | Nullable |
| solar_generation_gwh | numeric(12,2) | Solar generation. | Nullable |
| wind_generation_gwh | numeric(12,2) | Wind generation. | Nullable |
| total_installed_capacity_mw | numeric(12,2) | Total installed generation capacity. | Nullable |
| total_dependable_capacity_mw | numeric(12,2) | Total dependable capacity. | Nullable |
| created_at | timestamp with time zone | Record creation timestamp. | DEFAULT now() |
| updated_at | timestamp with time zone | Record update timestamp. | DEFAULT now() |

Relationships: Standalone time-series table. Updated via trigger trg_national_energy_annual_updated which sets updated_at to now() on each update. Row Level Security enabled; public read allowed, authenticated write allowed.

Table 9. hydropower_suitability

Purpose: Stores terrain-derived hydropower suitability metrics for each municipality, computed by the terrain analysis pipeline.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| municipality_id | integer | Parent municipality identifier. | PRIMARY KEY, FOREIGN KEY references municipalities(municipality_id) ON UPDATE CASCADE ON DELETE RESTRICT |
| province_id | integer | Parent province identifier. | NOT NULL, FOREIGN KEY references provinces(province_id) ON UPDATE CASCADE ON DELETE RESTRICT |
| municipality_name | text | Municipality name (denormalized for query convenience). | NOT NULL |
| province | text | Province name (denormalized for query convenience). | NOT NULL |
| latitude | double precision | Municipality latitude. | Nullable |
| longitude | double precision | Municipality longitude. | Nullable |
| elevation_m | double precision | Point elevation from DEM sampling. | Nullable |
| mean_elevation_m | double precision | Mean elevation within municipal buffer. | Nullable |
| min_elevation_m | double precision | Minimum elevation within municipal buffer. | Nullable |
| max_elevation_m | double precision | Maximum elevation within municipal buffer. | Nullable |
| elevation_range_m | double precision | Elevation range (max - min). | Nullable |
| mean_slope_deg | double precision | Mean terrain slope in degrees. | Nullable |
| hydraulic_head_m | double precision | Estimated hydraulic head (elevation range proxy). | Nullable |
| terrain_ruggedness | double precision | Terrain ruggedness index. | Nullable |
| watershed_gradient | double precision | Watershed steepness proxy (head / buffer distance). | Nullable |
| hydro_suitability_score | double precision | Composite hydropower suitability score (0-1). | Nullable |
| estimated_hydropower_potential_kw | double precision | Estimated micro-hydropower potential in kilowatts. | Nullable |
| runoff_potential | double precision | Normalized runoff potential (0-1). | Nullable |
| gravity_flow_potential | double precision | Normalized gravity flow feasibility (0-1). | Nullable |
| terrain_flatness | double precision | Flatness measure (1 - normalized slope). | Nullable |
| slope_classification | text | Categorical slope class (flat, gentle, moderate, steep, very_steep). | Nullable |
| elevation_classification | text | Categorical elevation class (low, mid, high, very_high). | Nullable |
| ridge_elevation | double precision | Maximum elevation within buffer (ridge proxy). | Nullable |
| terrain_exposure_index | double precision | Terrain exposure index (max_elev - mean_elev) / ruggedness. | Nullable |

Relationships: Many-to-one with municipalities and provinces. Indexed on province_id and municipality_name for filtering.

Table 10. ml_model_registry

Purpose: Registry of trained forecasting models. Ensures version control and active model selection.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| model_id | uuid | Unique model identifier. | PRIMARY KEY, DEFAULT gen_random_uuid() |
| model_name | text | Human-readable model name. | NOT NULL |
| model_version | text | Semantic version string. | NOT NULL |
| model_type | text | Algorithm type. | NOT NULL, CHECK (model_type IN ('SARIMA', 'LightGBM', 'XGBoost', 'Prophet')) |
| target_variable | text | Variable being forecasted. | NOT NULL |
| train_date | date | Date the model was trained. | NOT NULL |
| metrics | jsonb | Serialized performance metrics (MAE, RMSE, MAPE, R2). | Nullable |
| model_path | text | File path or URI to stored model artifact. | Nullable |
| is_active | boolean | Whether this model is currently serving predictions. | DEFAULT false |
| created_at | timestamp with time zone | Record creation timestamp. | DEFAULT now() |
| updated_at | timestamp with time zone | Record update timestamp. | DEFAULT now() |

Relationships: Standalone registry table. Unique partial index on (target_variable, is_active) where is_active = true, ensuring only one active model per target. Foreign key parent for forecast_cache. Updated via trigger trg_ml_model_registry_updated. Row Level Security enabled; public read allowed, authenticated write allowed.

Table 11. forecast_cache

Purpose: Cached forecast results per model, target variable, and horizon. Managed by application logic with TTL (e.g., 24 hours) to balance freshness and performance.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| forecast_id | uuid | Unique forecast record identifier. | PRIMARY KEY, DEFAULT gen_random_uuid() |
| model_id | uuid | Parent model identifier. | NOT NULL, FOREIGN KEY references ml_model_registry(model_id) ON DELETE CASCADE |
| target_variable | text | Variable being forecasted. | NOT NULL |
| horizon_years | smallint | Forecast horizon in years. | NOT NULL, CHECK (horizon_years > 0 AND horizon_years <= 10) |
| forecast_year | smallint | Specific year being forecasted. | NOT NULL |
| forecast_month | smallint | Specific month being forecasted (1-12). | Nullable, CHECK (forecast_month IS NULL OR (forecast_month >= 1 AND forecast_month <= 12)) |
| predicted_value | numeric(14,4) | Forecasted value. | NOT NULL |
| lower_bound | numeric(14,4) | Lower confidence interval bound. | Nullable |
| upper_bound | numeric(14,4) | Upper confidence interval bound. | Nullable |
| created_at | timestamp with time zone | Record creation timestamp. | DEFAULT now() |

Relationships: Many-to-one with ml_model_registry. Indexed on model_id, target_variable, forecast_year, forecast_month, and created_at for fast cache lookup and eviction. Row Level Security enabled; authenticated read and write allowed.

Table 12. chart_ai_insights

Purpose: Caches AI-generated insights for charts to reduce LLM API latency and cost.

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| id | uuid | Unique insight identifier. | PRIMARY KEY, DEFAULT gen_random_uuid() |
| chart_type | text | Type of chart being explained. | NOT NULL |
| chart_data_hash | text | MD5 hash of canonical chart data for cache matching. | NOT NULL |
| insight | text | Generated insight text. | NOT NULL |
| created_at | timestamp with time zone | Record creation timestamp. | DEFAULT now() |

Relationships: Standalone cache table. Composite index on (chart_type, chart_data_hash) for cache hit lookup. No foreign keys.

Table 13. regional_lookup (View)

Purpose: Provides a unified denormalized view of the geographic hierarchy for frontend location selection.

| Field | Type | Description |
|-------|------|-------------|
| region_id | integer | Region identifier. |
| region_name | text | Region name. |
| region_lat | double precision | Region latitude. |
| region_lon | double precision | Region longitude. |
| province_id | integer | Province identifier. |
| province_name | text | Province name. |
| province_lat | double precision | Province latitude. |
| province_lon | double precision | Province longitude. |
| municipality_id | integer | Municipality identifier. |
| municipality_name | text | Municipality name. |
| municipality_lat | double precision | Municipality latitude. |
| municipality_lon | double precision | Municipality longitude. |
| barangay_id | integer | Barangay identifier. |
| barangay_name | text | Barangay name. |
| barangay_lat | double precision | Barangay latitude. |
| barangay_lon | double precision | Barangay longitude. |

Relationships: Joins regions, provinces, municipalities, and barangays through their foreign key relationships.


9.7.2.2.8. Algorithm Structure

The following sections describe the core computational algorithms implemented within LUMI, presented in paragraph form to explain their purpose and application within the system.

Solar Temperature Factor Calculation

The system adjusts photovoltaic output for deviations from the standard test condition temperature of 25 degrees Celsius. Solar panel efficiency decreases as cell temperature rises above this reference, and the temperature factor quantifies this loss as a linear function of temperature deviation. Given a mean air temperature and a conservative industry-standard temperature coefficient of negative 0.004 per degree Celsius for crystalline silicon panels, the factor is computed and clamped at a minimum of zero to prevent negative power estimates. Philippine ambient temperatures frequently exceed 25 degrees Celsius in lowland municipalities, so without this correction, solar output estimates would be systematically optimistic. This factor is aggregated with other system losses within the solar performance ratio computation in the Ecosim module before daily and monthly energy output is calculated.

Solar Performance Ratio Aggregation

Real-world solar installations experience losses from temperature, dust accumulation, inverter inefficiency, cell mismatch, wiring resistance, and long-term degradation. The performance ratio combines these individual loss factors multiplicatively to obtain an overall system efficiency multiplier, floored at zero to prevent invalid values. This ratio typically falls between 0.5 and 0.85 for residential installations and is the standard metric in photovoltaic engineering for translating theoretical irradiance-based output into realistic expectations, consistent with IEC 61724 guidelines. Within LUMI, dust loss and degradation loss are optionally adjusted by wind speed and humidity before aggregation, allowing the simulation to respond to local climate conditions. The result is passed to the renewable energy calculator in the Ecosim module.

Solar Energy Output Calculation

The system converts solar irradiance data into electrical energy production using the peak power capacity of the installed array and the aggregated performance ratio. The algorithm first computes the array capacity in kilowatts-peak from the panel wattage and quantity, then multiplies this by daily solar irradiance and the performance ratio to obtain daily output. Monthly output is derived by scaling daily output over the number of days in the month. A solar suitability score is derived by normalizing irradiance against a theoretical maximum and capping the result at 100 even under extreme irradiance. This is the fundamental photovoltaic energy estimation formula used worldwide, requiring only irradiance from NASA POWER, system size, and performance ratio, making it suitable for household-level estimation without site-specific shading analysis. LUMI applies this algorithm within the Ecosim module using a default configuration of two 400-watt panels to represent a modest residential starter system.

Wind Power Output Calculation

The algorithm applies the fundamental wind power equation, which states that kinetic power in wind scales with the cube of wind speed, the swept area of the rotor, and air density. The system validates that rotor radius and wind speed are positive, air density falls within realistic bounds, and the power coefficient does not exceed the Betz limit of 0.593. Swept area is computed from the rotor radius, and rated power is derived by combining air density, swept area, wind speed cubed, the power coefficient, and overall mechanical-electrical efficiency. Realistic energy production accounts for variable wind conditions through a capacity factor, which addresses the critical distinction between rated power at ideal wind speed and actual energy production averaged over time, preventing the common error of assuming continuous operation at rated power. This algorithm is called by the renewable energy calculator in the Ecosim module using average rotor radius and power coefficient derived from small wind turbine product databases.

Runoff Coefficient Estimation

Based on Javadinejad et al. (2022), the runoff coefficient for small catchments varies with land slope because steeper terrain generates faster overland flow and less infiltration. Given mean terrain slope in degrees, the coefficient is determined through piecewise classification: gentle slopes below 3 degrees representing forested or pasture land receive a coefficient of 0.30, moderate slopes between 3 and 10 degrees representing mixed land use receive 0.45, steep slopes between 10 and 20 degrees representing cultivated or hilly terrain receive 0.60, and very steep slopes above 20 degrees representing rocky or urban surfaces receive 0.75. Ungauged small catchments in the Philippines typically lack streamflow measurements, so this coefficient method, combined with monthly precipitation from NASA POWER, provides a first-order estimate of available water flow for micro-hydropower sizing. The algorithm is invoked during the hydropower design flow estimation process in the Ecosim module.

Micro-Hydropower Design Flow Estimation

This algorithm adapts the rational method for small catchments to estimate the design flow rate at a micro-hydropower intake. The procedure converts catchment area and monthly rainfall depth into consistent units, obtains a base runoff coefficient from the slope-based estimation algorithm, then adjusts it by terrain suitability factors including runoff potential and watershed gradient. Total monthly runoff volume is computed from the effective runoff coefficient, precipitation depth, and catchment area. Average flow is obtained by dividing the runoff volume by the total seconds in a month, and the design flow incorporates a 40 percent environmental reserve and gravity-flow feasibility before being clamped to a realistic micro-hydro intake range. The 40 percent environmental reserve follows standard practice for run-of-river systems to maintain downstream ecology, and the default catchment area represents a typical small hillside drainage accessible to a household installation. The algorithm is called by the renewable energy calculator in the Ecosim module using terrain metrics retrieved from the hydropower suitability table.

Micro-Hydropower Electrical Output Calculation

The standard hydropower equation for run-of-river micro-hydro systems computes available electrical power from design flow and hydraulic head. The flow rate is first clamped to a realistic micro-hydro range, and the hydraulic head is scaled to 12 percent of the municipal elevation range to represent the local intake-to-turbine drop accessible to a single household, bounded between 2 and 25 meters. Hydraulic power is derived from water density, gravity, flow rate, and the realistic head, then multiplied by the combined turbine and generator efficiency to obtain electrical power. Daily and monthly energy follow by scaling electrical power over time. A hydro suitability score is derived by normalizing monthly energy against a reference value for rural micro-hydro systems. The 12 percent head scaling reflects that only a fraction of the total municipal elevation difference is accessible to a single household intake. The algorithm is called by the renewable energy calculator in the Ecosim module after flow rate estimation.

Economic Viability and Recommendation Scoring

For each renewable source, the system computes economic indicators and a composite suitability score to enable the Ecosim module to recommend the best option. The algorithm first caps usable generation at actual consumption to prevent overestimation of financial benefit. Monthly savings are derived from displaced consumption and the local electricity rate. System size is estimated conservatively using a Philippine national average of 4 equivalent peak-sun hours per day, and installation cost is computed from the system size and per-kilowatt pricing. The simple payback period divides installation cost by annual savings. The energy coverage ratio compares estimated generation against consumption, and the weighted suitability score combines 60 percent energy coverage with 40 percent source quality, following the weighted linear combination approach used in GIS-MCDA renewable energy site-selection studies. Carbon displacement is computed using the DOE 2019-2021 National Grid Emission Factor. The simple payback period is the dominant first-screening metric in residential photovoltaic techno-economic studies. This algorithm is called for each of solar, wind, and hydro options, then aggregated to select the highest-scoring recommendation in the Ecosim dashboard response builder.

ARIMA Time-Series Forecasting

An AutoRegressive Integrated Moving Average model with order one-one-one projects future national energy consumption and peak demand using historical annual data. The model captures trend and short-term autocorrelation in the first-differenced series, where the original time-series of consumption or peak demand is differenced once to remove non-stationarity, and the resulting series is modeled as a combination of an autoregressive term, a moving average term, and white noise. The model was trained offline using the statsmodels library with maximum likelihood estimation on Philippine national energy statistics from 2003 to 2020. Forecasts for 2025 to 2030 were generated with 95 percent confidence intervals and exported to comma-separated value artifacts. ARIMA provides a strong statistical baseline for national-level time-series forecasting; its interpretability and requirement for only the target variable, without exogenous predictors, make it suitable when macroeconomic drivers are not available at sufficient temporal resolution. The artifacts are loaded at runtime by the machine learning prediction service and served through the EnergyHub service.

Composite Renewable Potential Score for Choropleth Mapping

To support the provincial choropleth map in the EnergyHub dashboard, the system aggregates municipal climate and terrain data into a single renewable potential score. For each province, average solar irradiance, average wind speed, and average hydropower suitability are combined using weighted linear combination. Each component is normalized against its theoretical maximum, then weighted and summed: solar receives the largest weight at 40 percent, while wind and hydropower each receive 30 percent. The resulting composite score is scaled to a 0 to 100 range and rounded to two decimal places. The weighting reflects that solar irradiance is the most spatially variable and readily exploitable resource at the residential scale in the Philippines, while wind and hydropower contributions vary more strongly by local geography. This score enables intuitive choropleth mapping while reflecting the multi-source nature of renewable energy potential. It is computed within the renewable potential map builder in the EnergyHub service.


9.7.2.2.9. AI Tools and API

Google Gemini API

Google Gemini API was integrated into LUMI to provide natural language understanding and generation capabilities for the AI assistant component. The API processes user queries related to renewable energy, climate data, national energy statistics, and energy demand forecasts, and generates informative responses that complement the quantitative outputs of the machine learning, statistical, and physics-based calculation modules.

The AI assistant serves as an interactive decision support component that helps users understand renewable energy concepts, interpret forecast results, evaluate their municipal renewable potential, and receive contextual recommendations. Unlike static reports, the AI assistant can engage in conversational exchanges, adapt its explanations to the user's level of technical expertise, and address questions that fall outside the predefined scope of the dashboard visualizations.

The AI assistant receives natural language queries from users through the frontend interface. These queries are preprocessed to detect intent, extract relevant entities (e.g., region names, energy source types, time periods), and enrich the prompt with contextual data retrieved from the system's knowledge base. For chart-specific queries, the system computes a stable MD5 hash of the canonical chart data and checks the chart_ai_insights cache table. If a cached insight exists, it is returned directly to minimize latency and API cost. If no cache hit occurs, the enriched prompt is transmitted to the Gemini API. The generated response is postprocessed to ensure formatting consistency, verify factual grounding against system data where applicable, extract narrative content from JSON wrappers if present, and filter inappropriate content. The final response is delivered to the user through the chat interface and simultaneously stored in the cache table, with a maximum of three variants per chart hash to prevent unbounded growth.

The AI assistant plays a complementary role to the quantitative prediction modules. While the forecasting models provide numerical projections of energy demand and the Ecosim module provides renewable potential estimates, the AI assistant interprets these projections in accessible language, explains the factors influencing the predictions, and guides users through what-if scenarios.

The system employs prompt engineering techniques to structure API inputs for optimal response quality. Prompts are designed to include system context (e.g., latest DOE statistics, ARIMA forecasts), user query, relevant retrieved knowledge chunks from the FAISS vector database when RAG is enabled, and explicit instructions regarding response format, length, and tone. For comprehensive insights, structured multi-paragraph prompts specify required analytical themes including ASEAN context, renewable share discussion, infrastructure implications, and policy recommendations.

Groq API

Groq API was integrated as an alternative and complementary large language model inference provider for the AI assistant features. Groq provides high-performance inference capabilities that can be used to process user queries when the primary API is unavailable or when comparative response generation is needed. The integration follows the same input-output flow as the Gemini API, with queries being preprocessed, enriched with context, and postprocessed before delivery to the user.

The system handles API errors, rate limits, and fallback mechanisms to maintain service availability. When one API provider experiences downtime or rate limiting, the system can automatically switch to the alternative provider, ensuring continuous AI assistant functionality.

Evaluating LLM outputs requires approaches distinct from traditional classification accuracy metrics. Since the AI assistant generates free-text responses rather than discrete labels, its performance is assessed through the following dimensions: response correctness, verifying that factual claims align with system data and established domain knowledge; relevance, assessing whether the response directly addresses the user's query and provides useful information for renewable energy decision-making; ground truth comparison, comparing responses against reference answers prepared by domain experts for a set of benchmark questions; expert validation, where energy practitioners or academic experts rate responses on accuracy, completeness, and clarity using Likert scales or rubric-based scoring; hallucination checking, detecting fabricated facts, unsupported numerical claims, or contradictory statements in generated responses through automated fact-checking against system data and manual review of sample outputs; response time, measuring end-to-end latency from query submission to response completion to ensure interactions remain fluid and usable; and token and resource usage, monitoring API token consumption and associated costs to ensure sustainable operation within project resource constraints.

The evaluation of the AI assistant relies on benchmark question sets, expert review panels, and user feedback rather than traditional accuracy metrics such as precision or recall, which are not applicable to generative text tasks.

9.7.2.2.10. User Authentication and Role-Based Access Control

LUMI implements a single sign-on authentication flow using Supabase Auth, which supports email-password registration and Google OAuth. Upon successful registration, a database trigger named `handle_new_user` automatically inserts a row into the `profiles` table with the user's full name extracted from auth metadata, a row into the `user_roles` table with the default role of `user`, and a row into the `user_usage_limits` table with the default plan `free`. This ensures that every authenticated user has an associated profile and role without requiring manual intervention.

The backend validates JSON Web Tokens on every protected request through a `get_verified_user` dependency. This dependency extracts the Bearer token from the Authorization header, verifies its signature and expiration, and confirms that the user's email address has been verified. If any check fails, the request returns HTTP 401 or 403. All non-public API endpoints including EcoSim, EnergyHub, and Geothermal routes now enforce this dependency, ensuring that only authenticated users can access analytical features.

Role-based access control extends the basic authentication layer. The `user_roles` table stores a single role per user, drawn from an enumerated type `app_role` with values `user`, `admin`, and `dev`. A `_get_user_role` helper queries this table on every request to determine privilege level. The `require_admin` dependency returns HTTP 403 for any authenticated user whose role is not `admin` or `dev`. Admin routes under `/api/v1/admin` are protected by this dependency, preventing unauthorized access to user management, analytics, and system configuration endpoints.

On the frontend, the `AuthContext` provider fetches the user's role from Supabase whenever the session changes and exposes an `isAdmin` boolean. A `ProtectedRoute` wrapper component redirects unauthenticated visitors to `/login`, preserving the original destination in navigation state. An `AdminRoute` wrapper performs the same authentication check and additionally redirects non-admin users to `/dashboard`. The navbar conditionally renders an "Admin" link only when `isAdmin` is true, keeping the admin portal hidden from standard users.

9.7.2.2.11. Saved Simulation and Location Persistence

Authenticated users can persist EcoSim simulation inputs and results through the `saved_simulations` table. Each row stores the user ID, an optional label, the municipality ID, the original input parameters as JSONB, and the computed results as JSONB. This enables users to revisit prior analyses, compare configurations over time, and build a personal project history. The `saved_locations` table allows users to bookmark municipalities of interest, storing only the user ID, municipality ID, and an optional label. A unique constraint on `(user_id, municipality_id)` prevents duplicate bookmarks.

Both tables are protected by Row-Level Security policies that restrict SELECT, INSERT, UPDATE, and DELETE operations to rows where `auth.uid() = user_id`. This guarantees that users can only access their own data even if they craft direct Supabase client queries. The Decision Dashboard queries these tables to populate the "Saved Projects" and "Saved Locations" panels, enabling one-click navigation back to prior simulations.

9.7.2.2.12. AI Chatbot Architecture

The LUMI AI Assistant is a Retrieval-Augmented Generation system that combines semantic search over a structured knowledge base with large language model generation. When a user submits a query through the chat interface, the backend first encodes the query text into a dense vector embedding using the `all-MiniLM-L6-v2` sentence-transformer model. The embedding is compared against a pre-built FAISS index of chunked knowledge documents using cosine similarity, and the top-k most relevant chunks (default k=5) are retrieved.

These retrieved chunks are injected into a structured system prompt alongside the user's query. The prompt includes an explicit instruction to ground responses in the retrieved context and to cite sources using `[Source N]` notation. For authenticated users, the prompt builder also appends the user's saved simulations and saved locations as supplementary context, enabling personalized recommendations such as "Given your bookmarked municipality of Calamba and your saved solar simulation..."

The prompt is then sent to the Google Gemini API via the existing `gemini_funcs` module. The generated response is returned to the frontend and persisted in the `chat_messages` table alongside the retrieved chunk texts. Each conversation belongs to a `chat_session`, which groups messages under a user-generated title. The `chat_sessions` and `chat_messages` tables are protected by Row-Level Security policies that enforce ownership through session-level foreign key checks.

9.7.2.2.13. Decision Dashboard Design

The Decision Dashboard replaces the previous placeholder dashboard with a personalized analytical interface. Upon loading, the dashboard queries the user's `saved_locations` and `saved_simulations` from Supabase and renders them in dedicated panels. The Overview Card displays a composite renewable score gauge computed by normalizing and averaging the municipality-level solar, wind, hydro, and geothermal suitability scores. Each component is fetched from the respective pre-computed suitability tables and weighted equally in the composite.

The Recommendations section ranks renewable sources for the currently selected municipality using a weighted multi-criteria scoring function. The function considers estimated generation potential (40%), simple payback period (30%), and carbon reduction impact (30%). The top three sources are displayed with call-to-action buttons that pre-populate the EcoSim form. The Analytics Mini-Chart overlays national DOE consumption trends from the `energy_statistics` table with municipality-specific climate-adjusted projections, allowing users to contextualize local potential against national demand patterns.

9.7.2.2.14. Admin Portal

The admin portal provides operational oversight for the LUMI platform. It is accessible only to users whose `user_roles` entry is `admin` or `dev`. The frontend hides the admin navigation link from non-administrative users, and the backend rejects all unauthorized requests with HTTP 403.

The portal comprises four modules. User Management displays a paginated table of registered users drawn from the `profiles` and `user_roles` tables, showing name, role, plan, and account status. Analytics aggregates system-level metrics including total registered users, total saved simulations, total chat sessions, and the distribution of free versus premium plans. System Configuration allows administrators to toggle the chatbot availability, enable maintenance mode, and adjust free-tier limits for chat messages and saved simulations. All configuration changes are persisted to a `system_config` key-value table. Content Moderation provides a read-only view of recent chat sessions and messages for review.

Every administrative action is logged to the `admin_audit_log` table, which records the admin user ID, the action type, the target user ID (if applicable), and a JSONB details payload. This audit trail ensures accountability and traceability for all privileged operations.

Table X. Free vs Premium Feature Matrix

| Feature | Free Tier | Premium Tier |
|---------|-----------|--------------|
| EcoSim simulations | 3 saved | Unlimited |
| Saved locations | 1 municipality | Unlimited |
| AI chatbot | 5 messages/month | Unlimited |
| PDF report export | Watermarked | No watermark |
| Advanced recommendations | Basic ranking | Full multi-criteria with sensitivity |
| What-if forecasting | View only | Adjustable assumptions |
| Price | ₱0 | ₱199/month (Researcher) / ₱499/month (Planner) |

The free tier is designed to demonstrate core value while encouraging conversion through saved-project loss aversion. The premium tiers are architected in the database schema and middleware but do not require live payment processing for the thesis defense.

Table X. Database Schema Additions for Auth, Chatbot, Dashboard, and Admin Features

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| user_roles | Role-based access control | user_id (PK, FK auth.users), role (enum), created_at |
| profiles | Extended user profile | id (PK, FK auth.users), full_name, avatar_url, organization, location, preferred_municipality_id, plan, is_active |
| saved_simulations | Persisted EcoSim results | id (PK), user_id (FK), label, municipality_id, inputs (JSONB), results (JSONB), created_at |
| saved_locations | Bookmarked municipalities | id (PK), user_id (FK), municipality_id, label, created_at, UNIQUE(user_id, municipality_id) |
| chat_sessions | Chat conversation grouping | id (PK), user_id (FK), title, created_at |
| chat_messages | Individual chat messages | id (PK), session_id (FK), role, content, retrieved_chunks (JSONB), created_at |
| user_usage_limits | Monthly usage tracking | user_id (PK, FK), chat_messages_this_month, simulations_this_month, plan |
| admin_audit_log | Administrative action log | id (PK), admin_id (FK), action, target_user_id (FK), details (JSONB), created_at |

9.7.3. Testing Procedures

9.7.3.1. System Test Plan

Table 14. LUMI System Test Plan

| Aspect | Description |
|--------|-------------|
| Objective | Stress test the system to ensure robustness under multitasking conditions. Test all modules significant for forecasting accuracy, AI assistant quality, Ecosim calculation correctness, terrain pipeline integrity, and visualization performance. Ensure the system is ready before releasing it to users. |
| Test Scope | The test covers core functionalities of the environmental intelligence platform, including user interface, data processing pipelines, machine learning forecasting modules, Ecosim renewable energy calculations, terrain analysis pipeline, AI assistant integration, and performance under normal usage. |
| Testing Approach | The testing environment consists of the researchers' personal laptops and desktop computers, each configured to simulate various user conditions. The system is deployed across multiple devices to observe its behavior in different operating systems, browsers, and screen resolutions. This setup allows for a controlled yet diverse testing scenario, ensuring that the platform's performance remains stable and consistent across different hardware and software environments. |
| Test Environment | The testing is conducted internally by the researchers, using individual accounts to simulate multiple user experiences. Each researcher performs repeated testing cycles to evaluate the system's responsiveness, reliability, and overall functionality. Features are tested under various usage scenarios, including different user roles and interactions. The repeated trials aim to identify bugs, compatibility issues, and performance bottlenecks before the platform is released to a wider audience. |

Machine Learning Model Testing

The primary objectives of machine learning model testing are to evaluate the predictive performance of forecasting and estimation models, compare the effectiveness of different algorithms, and ensure that models generalize well to unseen data. Testing also aims to validate that model outputs are stable, reproducible, and suitable for decision support.

Since LUMI's forecasting modules predict continuous numerical values (e.g., energy demand in gigawatt-hours, peak demand in megawatts), regression-oriented metrics are employed. Mean Absolute Error (MAE) provides the average absolute difference between predicted and actual values, offering an intuitive measure of prediction error in the original units of the target variable. Mean Squared Error (MSE) represents the average squared difference between predicted and actual values, penalizing larger errors more heavily than MAE. Root Mean Square Error (RMSE) is the square root of MSE, expressed in the original units of the target variable, and is commonly used for comparing model performance across studies. Mean Absolute Percentage Error (MAPE) represents the average absolute percentage difference between predicted and actual values, facilitating comparison across datasets with different scales. The coefficient of determination (R-squared) indicates the proportion of variance in the dependent variable explained by the model.

Classification metrics such as accuracy, precision, recall, and F1-score are not appropriate for LUMI because the core forecasting tasks are formulated as regression problems predicting continuous energy output and demand values rather than discrete class labels. Applying classification metrics would require arbitrary binning of continuous predictions, which would lose granularity and potentially misrepresent model performance. Therefore, regression metrics are prioritized, with classification metrics reserved for any explicitly categorical subtasks that may be introduced.

Models are evaluated using temporal train-test splits and time-series cross-validation to ensure that temporal ordering is respected and that models are tested on future periods not seen during training. This prevents data leakage and provides realistic estimates of forecasting accuracy. The ARIMA(1,1,1) model was trained on 2003-2020 data and tested on 2021-2024 hold-out data.

Computational Performance Testing

Computational performance testing evaluates the efficiency and resource utilization of LUMI under representative operating conditions. Response time is measured as the elapsed time between a user request and the completion of the system's response, measured at both the API level and frontend level to identify bottlenecks. Memory utilization tracks the amount of RAM consumed by backend services, data processing pipelines, terrain raster analysis, and model inference operations during peak and average load conditions. CPU utilization monitors the percentage of CPU resources consumed during data processing, model training, terrain pipeline execution, and API request handling. Processing time measures the time required to complete batch operations such as model training, dataset ingestion, terrain metric computation, and report generation, distinguished from user-facing response time to assess backend efficiency.

Performance benchmarks are established by measuring each metric under controlled conditions with documented input sizes and request volumes. Baseline measurements are recorded for comparison against optimization efforts in subsequent iterations.

LLM Evaluation Testing

The evaluation of the Google Gemini and Groq API integrations requires specialized testing plans that account for the generative and nondeterministic nature of large language model outputs. A structured benchmark question set is prepared covering a range of query types including factual questions about renewable energy, interpretation of forecast results, recommendation requests, Ecosim output explanation, and clarification follow-ups. Each benchmark question has a reference answer prepared by the researchers based on system data and domain knowledge.

The following dimensions are measured: response correctness, where responses are scored on a Likert scale by expert evaluators for factual accuracy; answer relevance, where evaluators assess whether the response addresses the user's intent and provides useful information for renewable energy decision-making; groundedness, verifying the degree to which responses are grounded in the system's data and retrieved knowledge context rather than relying solely on the LLM's parametric knowledge; hallucination rate, measuring the proportion of responses containing fabricated facts, unsupported numerical claims, or contradictory statements; expert validation score, where domain experts rate overall response quality on a standardized rubric encompassing accuracy, completeness, clarity, and usefulness; response latency, measuring the time from query submission to fully rendered response in milliseconds; and token consumption, tracking the number of input and output tokens consumed per query to estimate API usage costs and optimize prompt efficiency.

Traditional classification accuracy is not applicable to LLM evaluation because the AI assistant does not select from a fixed set of labels. Instead, it generates open-ended text where correctness is multidimensional and context-dependent. The evaluation therefore relies on benchmark comparisons, rubric-based expert scoring, and user satisfaction metrics.

System Testing

System testing validates the integrated functionality of LUMI as a complete application. Functional testing maps each functional requirement to one or more test cases specifying preconditions, input data, execution steps, and expected outcomes. Integration testing verifies that the frontend, backend, database, and external services interact correctly, with test scenarios including end-to-end workflows such as user login, region selection, data retrieval, forecast generation, Ecosim simulation execution, and AI assistant query handling. API testing validates backend endpoints for correctness of HTTP methods, response status codes, payload schema conformance, and error handling. User acceptance testing invites potential users and domain experts to perform predefined tasks using the system, recording their ability to complete tasks successfully, the time required, and their subjective satisfaction.

9.7.4. Deployment

During the deployment phase, the researchers conducted a series of testing and evaluation activities to ensure the platform's quality and readiness. This includes system controlled testing, evaluation testing, and usability testing with participants from the target user communities.

Environment and Hosting
The frontend application is deployed as a static site to a cloud hosting platform (Netlify or Vercel) that provides content delivery network distribution, automatic HTTPS, and continuous deployment from the version control repository. The backend services are deployed to a platform-as-a-service provider (Render, Railway, or AWS) that supports Python application hosting, environment variable management, and horizontal scaling.

The hosting environment is configured with separate production and staging instances. The staging instance serves as a pre-production environment for final validation before promoting changes to the production instance. Domain configuration, SSL certificates, and DNS records are established to ensure secure and accessible endpoints.

Database Deployment
The PostgreSQL database is hosted on Supabase, which provides managed database services, automatic backups, row-level security, and real-time subscriptions. Database migrations are version-controlled and applied through automated deployment pipelines to ensure schema consistency across environments. The schema includes tables for geographic hierarchy, climate data, energy statistics, terrain metrics, model registry, forecast cache, and AI insights.

External API Configuration
External API keys for Google Gemini and Groq are stored as encrypted environment variables and are never committed to version control. API rate limits are monitored, and fallback logic is implemented to switch between providers or degrade gracefully when limits are approached. The system retries transient failures with exponential backoff.

Security
The system implements standard security practices including HTTPS enforcement, secure authentication using JSON Web Tokens (JWT), input sanitization, and parameterized database queries to prevent injection attacks. CORS policies are configured to restrict frontend access to authorized domains. Supabase Row Level Security policies control access to sensitive tables, with public read access allowed for national energy statistics and model metadata, and authenticated write access restricted to administrators.

Monitoring
Application logs, error traces, and performance metrics are collected through the hosting platform's monitoring tools. Alert thresholds are configured for high error rates, elevated response times, and memory usage spikes. Regular log reviews are conducted to identify and resolve issues proactively.

Maintenance
A maintenance schedule is established for applying dependency updates, security patches, and model retraining. The model registry tracks model versions and performance history, enabling rollback to previous model versions if updated models exhibit degraded performance. Dataset refresh procedures are documented to ensure that the system's data remains current with new DOE publications, updated climate records from NASA POWER, and revised elevation data.


9.8. Testing and Evaluation

This section presents the comprehensive testing and evaluation plan for LUMI. The plan is structured as an initial test plan, meaning it documents objectives, approaches, procedures, test cases, metrics, and evaluation criteria without reporting final results. All testing activities are designed to validate functional correctness, computational accuracy, usability, system integration, and software quality according to internationally recognized standards.

9.8.1. Unit Testing

Purpose: To verify the correctness of individual functions, classes, and components in isolation before they are integrated into the larger system. Unit testing aims to detect logic errors, boundary condition failures, and incorrect return values at the earliest possible stage of development.

Testing Scope: The unit testing plan covers frontend components, backend API endpoints, data processing functions, authentication handlers, database operations, machine learning preprocessing pipelines, and renewable energy calculation modules including solar, wind, hydropower, and geothermal functions.

Methodology: Unit tests are implemented using the pytest framework for Python backend modules and the React Testing Library with Vitest (using jsdom) for frontend components. Tests are organized into test classes corresponding to functional modules. Fixtures provide reusable test data. Mocking is used to isolate components from external dependencies such as Supabase, NASA POWER API, Google Gemini API, and Groq API. Frontend tests are located in `react-frontend/src/components/__tests__/DashboardChart.test.jsx`; backend unit and integration tests are located in `lumi_tests/tests/unit/` and `lumi_tests/tests/integration/`.

Test Procedure: For each unit under test, the procedure involves (1) arranging the test environment and input data, (2) invoking the function or method with the prepared inputs, (3) capturing the actual output, and (4) asserting that the actual output matches the expected output within acceptable tolerance. Edge cases including None inputs, zero values, negative values, extreme values, and boundary conditions are explicitly tested.

Test Data/Input: Synthetic test datasets are created to represent realistic Philippine municipal climate profiles, DOE energy statistics, and terrain elevation samples. Fixture factories generate parameterized inputs for repeated test scenarios.

Expected Output: Each test asserts a specific expected value, exception, or state change. Tests pass when all assertions are satisfied; tests fail when any assertion is violated.

Evaluation Criteria: A module is considered unit-test compliant when its test suite achieves at least 80 percent statement coverage and all critical path functions (those directly affecting energy calculations, forecasts, or financial outputs) have dedicated test cases.

Sample Unit Test Cases

Table 15. Frontend Unit Test Cases

| Test ID | Module | Input | Expected Result | Status |
|---------|--------|-------|-----------------|--------|
| FE-001 | Dashboard Component | mock forecast data with years [2020,2021,2022] and values [100,110,120] | Renders a chart container with three data points | Implemented in `react-frontend/src/components/__tests__/DashboardChart.test.jsx` using Vitest |
| FE-002 | Region Selector | user types "Cebu" | Dropdown filters to municipalities containing "Cebu" | To be tested |
| FE-003 | Ecosim Form | monthly_consumption=0, monthly_bill=500 | Displays validation error: consumption must be greater than zero | To be tested |
| FE-004 | AI Chat Input | user submits empty query | Submit button disabled or error message displayed | Implemented in `react-frontend/src/components/__tests__/DashboardChart.test.jsx` using Vitest |
| FE-005 | Map Component | renewable_potential data with province scores | Choropleth map renders provinces with color gradients | To be tested |
| FE-006 | Trend Chart | historical series with 20 years | X-axis labels do not overlap; tooltip shows correct year | To be tested |

Table 16. Backend API Unit Test Cases

| Test ID | Module | Input | Expected Result | Status |
|---------|--------|-------|-----------------|--------|
| BE-001 | GET /energyhub/overview | None | Returns JSON with latest_consumption_gwh, latest_peak_demand_mw, latest_generation_gwh, and forecast_summary | To be tested |
| BE-002 | GET /energyhub/forecast?metric=consumption | metric="consumption" | Returns forecast years, values, confidence intervals, and model metadata (ARIMA, Linear Trend, or Holt) | Implemented in `test_api.py` as `test_forecast_consumption_metric` |
| BE-003 | GET /energyhub/forecast?metric=invalid | metric="invalid" | Returns 422 Unprocessable Entity or empty forecast with error | Implemented in `test_api.py` as `test_forecast_invalid_metric` |
| BE-004 | POST /ecosim/ | house_name="Test House", municipality="MALAY", current_electricity_bill=2500, electricity_rate=12.0, desired_savings=30.0 | Returns 201 with JSON containing solar, wind, hydro outputs and recommended_source | Implemented in `test_api.py` as `test_post_ecosim_valid_municipality` |
| BE-005 | POST /ecosim/ | house_name="Test House", municipality="INVALID_MUNICIPALITY_NAME", current_electricity_bill=2500, electricity_rate=12.0, desired_savings=30.0 | Returns 404 Not Found or 422 Unprocessable Entity | Implemented in `test_api.py` as `test_post_ecosim_invalid_municipality` |
| BE-006 | Authentication | valid JWT token in Authorization header | Request proceeds to protected endpoint | Implemented in `test_api.py` as `test_valid_jwt_access` |
| BE-007 | Authentication | expired or malformed JWT token | Returns 401 Unauthorized | Implemented in `test_api.py` as `test_expired_jwt_rejected` |

Table 17. Machine Learning Unit Test Cases

| Test ID | Module | Input | Expected Result | Status |
|---------|--------|-------|-----------------|--------|
| ML-001 | preprocess_energy_data | DataFrame with missing consumption values | Missing values filled via ffill().bfill(); year is integer | To be tested |
| ML-002 | create_time_features | Sorted DataFrame with years 2000-2010 | trend column is monotonic increasing; lag_1 equals previous year's consumption | To be tested |
| ML-003 | split_train_test | DataFrame with 10 rows, test_size=3 | train has 7 rows, test has 3 rows; test contains last rows | To be tested |
| ML-004 | linear_trend_forecast | Perfectly linear series (slope=100) | MAPE < 1.0 percent on test set | To be tested |
| ML-005 | calculate_mape | y_true=[100,200,300], y_pred=[110,190,330] | Returns approximately 8.333 | To be tested |
| ML-006 | calculate_mape | y_true=[0,0,0], y_pred=[1,2,3] | Returns NaN (zero values excluded) | To be tested |

Table 18. Renewable Energy Calculation Unit Test Cases

| Test ID | Module | Input | Expected Result | Status |
|---------|--------|-------|-----------------|--------|
| RE-001 | calculate_temperature_factor | avg_temp_c=25.0 | Returns 1.0 exactly | To be tested |
| RE-002 | calculate_temperature_factor | avg_temp_c=35.0 | Returns value < 1.0 and > 0.0 | To be tested |
| RE-003 | calculate_temperature_factor | avg_temp_c=300.0 | Returns 0.0 (clamped floor) | To be tested |
| RE-004 | calculate_dust_loss_from_wind | ws10m=3.0 | Returns approximately 0.97 | To be tested |
| RE-005 | calculate_dust_loss_from_wind | ws10m=20.0 | Returns value between 0.80 and 1.0 | To be tested |
| RE-006 | calculate_performance_ratio | default parameters | Returns product of all factors, floored at 0.0 | To be tested |
| RE-007 | solar_calc | panel_wattage=400, panels=2, irradiance=5.0, PR=0.75, days=30 | system_kwp=0.8; daily and monthly outputs > 0; score between 0 and 100 | To be tested |
| RE-008 | solar_calc | irradiance=10.0 (extreme) | solar_score capped at 100 | To be tested |
| RE-009 | calculate_wind_output | wind_speed=3.0, days=30, air_density=1.18 | rated_power_kw > 0; monthly_energy_kwh > 0 | To be tested |
| RE-010 | calculate_wind_output | wind_speed doubled from 3 to 6 m/s | rated_power_kw increases by approximately 8x | To be tested |
| RE-011 | calculate_wind_output | cp=0.60 | Raises ValueError with "Betz limit" message | To be tested |
| RE-012 | estimate_runoff_coefficient | slope_deg=2.0 | Returns 0.30 (gentle slope) | To be tested |
| RE-013 | estimate_runoff_coefficient | slope_deg=15.0 | Returns 0.60 (steep slope) | To be tested |
| RE-014 | estimated_flow_rate | rainfall=300 mm, moderate terrain factors | Returns value between 0.001 and 0.5 cms | To be tested |
| RE-015 | calculate_hydropower | flow_rate=0.1, head_m=15, days=30 | available_power_kw > 0; realistic_head_m between 2 and 25 | To be tested |
| RE-016 | calculate_hydropower | flow_rate=0.0 | All energy outputs equal 0.0; hydro_score equals 0.0 | To be tested |
| RE-017 | _calculate_option_summary | solar, generation=200, consumption=300, rate=10 | suitability_score between 0 and 1; payback_years > 0 | Implemented in `test_renewable_calculations.py` as `TestCalculateOptionSummary` with solar, wind, and geothermal scenarios |
| RE-018 | _haversine | lat1=14.5, lon1=120.9, lat2=14.5, lon2=120.9 | Returns 0.0 (same point) | Implemented in `test_geothermal_calculations.py` as `TestHaversine` |
| RE-019 | calculate_fault_distance | muni_lat=14.5, muni_lon=120.9, mock faults | Returns distance to nearest fault >= 0 | Implemented in `test_geothermal_calculations.py` as `TestFaultDistance` |
| RE-020 | calculate_fault_density | fault_length=45.0, area=150.0 | Returns 0.3 (faults per km2) | Implemented in `test_geothermal_calculations.py` as `TestFaultDensity` |
| RE-021 | calculate_volcano_distance | muni_lat=14.0, muni_lon=120.99, mock volcanoes | Returns distance to nearest volcano >= 0 | Implemented in `test_geothermal_calculations.py` as `TestVolcanoDistance` |
| RE-022 | calculate_heatflow_score | heat_flow=80.0 mW/m2 | Returns ~0.5 (mid-range of 40-120) | Implemented in `test_geothermal_calculations.py` as `TestHeatflowScore` |
| RE-023 | calculate_geothermal_gradient | heat_flow=80.0, conductivity=2.5 | Returns ~32.0 C/km | Implemented in `test_geothermal_calculations.py` as `TestGeothermalGradient` |
| RE-024 | calculate_reservoir_temperature | surface_temp=27.0, gradient=30.0, depth=2000 | Returns ~87.0 C | Implemented in `test_geothermal_calculations.py` as `TestReservoirTemperature` |
| RE-025 | calculate_aquifer_score | permeability=-14.0, porosity=0.20, thickness=800 | Returns score between 0 and 1 | Implemented in `test_geothermal_calculations.py` as `TestAquiferScore` |
| RE-026 | estimate_flow_rate | aquifer_score=0.5, permeability=-14.0 | Returns flow rate between 10 and 500 kg/s | Implemented in `test_geothermal_calculations.py` as `TestEstimateFlowRate` |
| RE-027 | compute_geothermal_suitability | muni_lat=14.5, muni_lon=120.9, surface_temp=28.0, mock datasets | Returns geothermal_score, classification, and all indicator scores | Implemented in `test_geothermal_calculations.py` as `TestComputeGeothermalSuitability` |
| RE-028 | compute_geothermal_output | surface_temp=27.0, gradient=30.0, aquifer_score=0.5, plant_type=binary | Returns thermal_power_mw, electric_power_mw, annual_energy_gwh, confidence_score | Implemented in `test_geothermal_calculations.py` as `TestComputeGeothermalOutput` |

9.8.2. Usability Testing

Purpose: To evaluate how effectively target users can learn to use LUMI, complete common tasks, and interpret the information presented by the system. Usability testing focuses on interface clarity, navigation efficiency, and user satisfaction.

Testing Scope: The usability testing plan covers dashboard navigation, forecast exploration, Ecosim simulation configuration, map interaction, chart interpretation, and AI assistant query formulation.

Methodology: A combination of task-based observation and post-task questionnaires is employed. Participants are asked to think aloud while completing predefined tasks. Observers record task completion times, error counts, help requests, and subjective comments. The System Usability Scale (SUS) and a custom Likert-scale questionnaire are administered after testing.

Test Procedure: Each participant attends a single 45-60 minute session. The session begins with a brief demographic questionnaire. The participant is then presented with the system and asked to complete a sequence of tasks of increasing complexity. The observer does not provide assistance unless the participant explicitly requests it or remains stuck for more than two minutes. After all tasks, the participant completes the SUS and the custom questionnaire.

Test Data/Input: Tasks are designed to require specific system capabilities without presuming technical expertise. Example tasks include: (1) "Find the total electricity consumption for the most recent year shown on the EnergyHub dashboard." (2) "Select your home municipality and generate a renewable energy recommendation using Ecosim." (3) "Explain what the choropleth map colors mean for renewable potential." (4) "Ask the AI assistant why solar energy might be recommended for your municipality."

Expected Output: For each task, the observer records whether the task was completed successfully, the time taken, the number of errors or missteps, and any verbal feedback. Questionnaire responses are collected on a 1-5 Likert scale.

Evaluation Criteria: Success is measured by task completion rate (target: >= 85 percent), average task time (target: <= 90 seconds for simple tasks, <= 5 minutes for complex tasks), SUS score (target: >= 68, above-average usability), and average Likert ratings (target: >= 4.0 for clarity and satisfaction).

Participants

The usability testing participants are recruited from the following groups to ensure diversity of technical background:
- Household decision-makers: Adults responsible for household energy bills, with no formal technical training in energy systems. This group represents the primary non-technical user base.
- Renewable energy professionals: Practitioners, consultants, or educators with domain expertise in solar, wind, or micro-hydro systems. This group validates whether the system presents information at an appropriate depth for informed users.
- Technical users: Students or researchers in computer science, engineering, or environmental science who can evaluate technical correctness and interface efficiency.

Testing Tasks

Task 1: Navigate to the EnergyHub dashboard and identify the most recent total electricity consumption value and the renewable energy share percentage.
Task 2: Explore the forecast chart and state whether electricity consumption is projected to increase or decrease by 2030.
Task 3: Open the Ecosim module, select a municipality, enter a monthly electricity bill and consumption value, and generate a renewable energy recommendation.
Task 4: Interpret the Ecosim results, including which renewable source is recommended, the estimated monthly generation, and the simple payback period.
Task 5: Navigate to the map visualization and identify which provinces have the highest renewable potential scores.
Task 6: Ask the AI assistant at least two questions about renewable energy and evaluate whether the responses are understandable and relevant.

Evaluation Metrics

Ease of Use: The extent to which users can operate the system without difficulty, measured by error frequency and help requests.
Learnability: The speed with which users achieve proficiency during their first session, measured by improvement in task time across sequential tasks.
Interface Clarity: The degree to which labels, icons, charts, and visual elements are self-explanatory, measured by comprehension questions.
User Satisfaction: Overall subjective impression of the system, measured by SUS score and Likert ratings.

Usability Questionnaire Structure

Section A: Demographics (age group, occupation, familiarity with renewable energy, internet usage frequency).
Section B: Task Experience (rate each task on difficulty from 1=Very Easy to 5=Very Difficult).
Section C: Interface Assessment (rate clarity of labels, chart readability, map usefulness, AI response quality on 1-5 scale).
Section D: Overall Satisfaction (rate likelihood to recommend, perceived usefulness, trust in recommendations on 1-5 scale).
Section E: Open Feedback (what did you like most, what should be improved, any confusing features).

9.8.3. System Testing

Purpose: To validate the integrated functionality of LUMI as a complete application, ensuring that all modules interact correctly, data flows are consistent, and the system behaves reliably under realistic usage patterns.

Testing Scope: The system testing plan covers complete user workflows, frontend-backend communication, database read/write operations, API reliability under load, ML pipeline execution from data retrieval to forecast serving, visualization rendering accuracy, Ecosim simulation end-to-end execution, and AI assistant query-response cycles.

Methodology: System testing is performed using a combination of automated integration tests, manual end-to-end walkthroughs, and performance benchmarks. Automated tests use pytest with HTTPX for API testing (`lumi_tests/tests/integration/test_api.py`), SQL assertions for database testing (`test_database.py`), pytest-benchmark for performance testing (`performance_test.py`), and fixture-based pipeline testing (`test_pipeline.py`). Manual tests follow scripted scenarios simulating real user journeys.

Test Procedure: For each test scenario, the procedure involves (1) initializing the system in a clean state, (2) executing the user journey step by step, (3) verifying intermediate states at each step, (4) checking final outcomes against expected results, and (5) recording any deviations or errors.

Test Data/Input: Test scenarios use a mix of real production data (anonymized if necessary) and carefully constructed synthetic data that exercises boundary conditions.

Expected Output: Each scenario produces a pass/fail determination based on whether all intermediate and final states match expectations.

Evaluation Criteria: The system is considered ready for pilot deployment when all critical-path scenarios pass, no high-severity defects remain open, API response times are within acceptable thresholds, and the system remains stable during a 30-minute continuous usage simulation.

Functional Testing Cases

ST-F-001: User Registration and Login
- Input: Valid email and password.
- Steps: Register account, verify email, log in, access protected dashboard.
- Expected: Account created, JWT issued, dashboard data loads.

ST-F-002: EnergyHub Dashboard Load
- Input: None (public endpoint).
- Steps: Navigate to dashboard, wait for data load.
- Expected: Latest statistics card displays current year, total consumption, renewable share, and capacity margin.

ST-F-003: Forecast Chart Display
- Input: Select "consumption" forecast.
- Steps: Click forecast tab, view chart.
- Expected: Chart shows historical years plus forecast years 2025-2030, with confidence interval shading.

ST-F-004: Ecosim Complete Workflow
- Input: Municipality="MALAY", monthly_consumption=300 kWh, monthly_bill=2500 PHP.
- Steps: Enter inputs, submit, view results.
- Expected: Results contain climate summary, solar/hydro/wind outputs, recommended source with suitability score, payback period, and carbon reduction.

ST-F-005: Map Visualization Load
- Input: Select "renewable_potential" metric.
- Steps: Navigate to map view.
- Expected: Choropleth map renders all provinces with color-coded scores; tooltip shows province name and score on hover.

Integration Testing Cases

ST-I-001: Frontend to Backend API Communication
- Input: Dashboard page load.
- Steps: Frontend requests /energyhub/overview.
- Expected: Backend responds within 2 seconds with valid JSON; frontend renders without errors.

ST-I-002: Backend to Database Query
- Input: Ecosim request for municipality data.
- Steps: Backend queries municipalities and hydropower_suitability tables.
- Expected: Database returns matching rows within 500 ms; foreign key relationships resolve correctly.

ST-I-003: ML Predictor Data Loading
- Input: Backend service startup.
- Steps: EnergyHubML loads CSV artifacts.
- Expected: All required CSV files are found and parsed; no NaN values in critical columns.

ST-I-004: AI Assistant with RAG Pipeline
- Input: User query with use_rag=true.
- Steps: Backend retrieves context from FAISS, builds enriched prompt, calls Gemini API.
- Expected: Response is generated, postprocessed, and returned within 5 seconds.

ST-I-005: Cache Read and Write
- Input: Repeated identical chart insight request.
- Steps: First request generates and stores insight; second request hits cache.
- Expected: Second response returns within 200 ms; database contains cached record.

Performance Testing Cases

ST-P-001: Concurrent API Load
- Input: 50 simultaneous requests to /energyhub/overview.
- Expected: 95th percentile response time < 2 seconds; no 5xx errors.

ST-P-002: Large Dataset Rendering
- Input: Historical trends chart with 20+ years of multi-series data.
- Expected: Frontend renders within 3 seconds; no browser freezing.

ST-P-003: Memory Utilization
- Input: Continuous Ecosim requests for 100 different municipalities.
- Expected: Backend RSS memory remains stable without monotonic growth; no memory leaks detected.

9.8.4. Pilot Run

Purpose: To conduct a controlled preliminary deployment of LUMI with real users from the target communities, gathering qualitative and quantitative feedback on system functionality, usability, and decision support value before formal evaluation.

Participants: A purposive sample of 15-25 participants representing household decision-makers, community leaders, students, and renewable energy professionals. Participants are selected to cover a range of technical backgrounds and geographic locations within the Philippines.

Environment: The pilot is conducted using the staging deployment of LUMI, hosted on the same infrastructure as the production environment but isolated from live user traffic. Participants access the system using their own devices (laptops, tablets, or smartphones) to ensure realism.

Procedure: The pilot run spans five days. Day 1 involves participant orientation and account creation. Days 2-4 involve self-directed exploration of the system, with participants encouraged to complete at least three Ecosim simulations, explore the EnergyHub dashboard, and interact with the AI assistant. Day 5 involves a structured feedback session where participants complete the ISO 25010 questionnaire, the SUS, and a semi-structured interview.

Data Collection: Quantitative data includes task completion rates, time-on-task, SUS scores, ISO 25010 ratings, and system-generated logs of feature usage. Qualitative data includes open-ended questionnaire responses, interview transcripts, and observation field notes.

Feedback Collection: Feedback is collected through four channels: (1) in-app feedback form with categorized issues, (2) post-session questionnaires, (3) semi-structured interviews, and (4) system analytics (page views, feature clicks, drop-off points).

Success Criteria: The pilot run is considered successful if: (1) at least 80 percent of participants complete the core Ecosim workflow without assistance, (2) the average SUS score is 68 or higher, (3) no critical defects (those preventing task completion) are discovered, (4) AI assistant responses are rated 4.0 or higher on average for relevance and clarity, and (5) average page load time across all devices is under 3 seconds.

The pilot results will support thesis evaluation by providing empirical evidence of the system's usability, functional completeness, and perceived value to target users. Participant quotes and aggregated metrics will be used to demonstrate that LUMI meets its design objectives.

9.8.5. Evaluation Rubrics (ISO/IEC 25010 Questionnaire)

Purpose: To evaluate LUMI against the ISO/IEC 25010:2011 software quality model using standardized criteria that cover functional suitability, performance efficiency, compatibility, usability, reliability, security, maintainability, and portability.

Methodology: Two parallel evaluation instruments are prepared: one for end users (focusing on functional suitability, usability, and satisfaction) and one for expert evaluators (focusing on performance efficiency, reliability, security, and maintainability). Both instruments use a 5-point Likert scale.

Rating Scale: 1 - Strongly Disagree, 2 - Disagree, 3 - Neutral, 4 - Agree, 5 - Strongly Agree.

Table 19. ISO/IEC 25010 Evaluation Criteria Table

| Category | Indicator | Description | Rating Scale |
|----------|-----------|-------------|--------------|
| Functional Suitability | Functional Completeness | The system provides all functions necessary for renewable energy decision support, including forecasting, simulation, visualization, and AI assistance. | 1-5 |
| Functional Suitability | Functional Correctness | The system's calculations (solar, wind, hydro, economic) produce accurate and physically plausible results. | 1-5 |
| Functional Suitability | Functional Appropriateness | The system functions align with the stated objectives of supporting renewable energy decisions for Philippine users. | 1-5 |
| Performance Efficiency | Time Behavior | The system responds to user actions within acceptable time limits (page load < 3s, API response < 2s, AI response < 5s). | 1-5 |
| Performance Efficiency | Resource Utilization | The system uses memory, CPU, and network resources efficiently during normal operation. | 1-5 |
| Performance Efficiency | Capacity | The system can handle the expected number of concurrent users and dataset sizes without degradation. | 1-5 |
| Compatibility | Co-existence | The system operates correctly alongside other web applications and browser extensions. | 1-5 |
| Compatibility | Interoperability | The system successfully exchanges data with external APIs (NASA POWER, Gemini, Groq) and databases (Supabase). | 1-5 |
| Usability | Learnability | Users can learn to operate the system effectively during their first session. | 1-5 |
| Usability | Operability | Users can operate and control the system with minimal effort. | 1-5 |
| Usability | User Interface Aesthetics | The interface is visually pleasing, consistent, and professionally designed. | 1-5 |
| Usability | Accessibility | The interface is usable across different devices and screen sizes, with readable fonts and adequate color contrast. | 1-5 |
| Reliability | Maturity | The system operates without crashes or unexpected terminations during normal use. | 1-5 |
| Reliability | Availability | The system is accessible when users need it, with minimal planned or unplanned downtime. | 1-5 |
| Reliability | Fault Tolerance | The system continues to function gracefully when external APIs are unavailable or inputs are invalid. | 1-5 |
| Reliability | Recoverability | The system can recover user data and session state after interruptions. | 1-5 |
| Security | Confidentiality | The system protects user data and prevents unauthorized access to personal information. | 1-5 |
| Security | Integrity | The system prevents unauthorized modification of data and forecasts. | 1-5 |
| Security | Authenticity | The system correctly identifies users and prevents impersonation. | 1-5 |
| Maintainability | Modularity | The system's architecture allows individual components to be modified without affecting others. | 1-5 |
| Maintainability | Reusability | Components and functions can be reused in other contexts or modules. | 1-5 |
| Maintainability | Analyzability | The system's code and data flows can be understood and diagnosed when defects occur. | 1-5 |
| Maintainability | Modifiability | Changes to requirements or data sources can be implemented with minimal effort. | 1-5 |
| Portability | Adaptability | The system can be adapted to different deployment environments or data sources. | 1-5 |
| Portability | Installability | The system can be deployed to cloud hosting platforms with minimal configuration. | 1-5 |
| Portability | Replaceability | Individual components (e.g., LLM provider, database host) can be replaced without redesigning the entire system. | 1-5 |

The ISO 25010 evaluation is conducted after the pilot run. End-user participants complete the Functional Suitability, Usability, and Reliability indicators. Expert evaluators (energy practitioners and software engineers) complete the Performance Efficiency, Compatibility, Security, Maintainability, and Portability indicators. Results are aggregated by category, and mean scores are computed for each indicator and overall quality characteristic.

