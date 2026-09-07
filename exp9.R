# Install packages if needed
# install.packages(c("shiny", "shinydashboard", "ggplot2",
#                    "plotly", "dplyr", "DT"))

library(shiny)
library(shinydashboard)
library(ggplot2)
library(plotly)
library(dplyr)
library(DT)

# ----------------------------
# Sample Dataset
# ----------------------------

set.seed(123)

students <- data.frame(
  Student_ID = paste0("S", sprintf("%03d", 1:100)),
  Name = paste("Student", 1:100),
  Department = sample(c("CSE", "ECE", "EEE", "ME"), 100, replace = TRUE),
  Semester = sample(1:8, 100, replace = TRUE),
  Subject = sample(
    c("Mathematics", "Programming", "Database",
      "Networks", "Statistics"),
    100,
    replace = TRUE
  ),
  Marks = sample(35:100, 100, replace = TRUE),
  Attendance = sample(50:100, 100, replace = TRUE)
)

students <- students %>%
  mutate(
    Result = ifelse(Marks >= 40, "Pass", "Fail"),
    Grade = case_when(
      Marks >= 90 ~ "A+",
      Marks >= 80 ~ "A",
      Marks >= 70 ~ "B",
      Marks >= 60 ~ "C",
      Marks >= 50 ~ "D",
      Marks >= 40 ~ "E",
      TRUE ~ "F"
    )
  )


# ----------------------------
# UI
# ----------------------------

ui <- dashboardPage(

  dashboardHeader(
    title = "Student Performance Dashboard"
  ),

  dashboardSidebar(

    sidebarMenu(

      menuItem(
        "Dashboard",
        tabName = "dashboard",
        icon = icon("dashboard")
      ),

      selectInput(
        "department",
        "Select Department",
        choices = c("All", unique(students$Department)),
        selected = "All"
      ),

      selectInput(
        "semester",
        "Select Semester",
        choices = c("All", sort(unique(students$Semester))),
        selected = "All"
      ),

      selectInput(
        "subject",
        "Select Subject",
        choices = c("All", unique(students$Subject)),
        selected = "All"
      )
    )
  ),

  dashboardBody(

    tabItems(

      tabItem(
        tabName = "dashboard",

        fluidRow(

          valueBoxOutput(
            "avgMarks",
            width = 3
          ),

          valueBoxOutput(
            "avgAttendance",
            width = 3
          ),

          valueBoxOutput(
            "passRate",
            width = 3
          ),

          valueBoxOutput(
            "studentCount",
            width = 3
          )
        ),

        fluidRow(

          box(
            title = "Subject-wise Average Marks",
            width = 6,
            plotlyOutput("subjectPlot")
          ),

          box(
            title = "Marks Distribution",
            width = 6,
            plotlyOutput("marksPlot")
          )
        ),

        fluidRow(

          box(
            title = "Attendance vs Marks",
            width = 6,
            plotlyOutput("attendancePlot")
          ),

          box(
            title = "Grade Distribution",
            width = 6,
            plotlyOutput("gradePlot")
          )
        ),

        fluidRow(

          box(
            title = "Student Academic Records",
            width = 12,
            DTOutput("studentTable")
          )
        )
      )
    )
  )
)


# ----------------------------
# SERVER
# ----------------------------

server <- function(input, output) {

  filteredData <- reactive({

    data <- students

    if (input$department != "All") {
      data <- data %>%
        filter(Department == input$department)
    }

    if (input$semester != "All") {
      data <- data %>%
        filter(Semester == input$semester)
    }

    if (input$subject != "All") {
      data <- data %>%
        filter(Subject == input$subject)
    }

    data
  })


  # Average Marks

  output$avgMarks <- renderValueBox({

    avg <- round(mean(filteredData()$Marks), 1)

    valueBox(
      paste(avg, "%"),
      "Average Marks",
      icon = icon("chart-line"),
      color = "blue"
    )
  })


  # Average Attendance

  output$avgAttendance <- renderValueBox({

    attendance <- round(
      mean(filteredData()$Attendance),
      1
    )

    valueBox(
      paste(attendance, "%"),
      "Average Attendance",
      icon = icon("user-check"),
      color = "green"
    )
  })


  # Pass Rate

  output$passRate <- renderValueBox({

    rate <- round(
      mean(filteredData()$Result == "Pass") * 100,
      1
    )

    valueBox(
      paste(rate, "%"),
      "Pass Rate",
      icon = icon("graduation-cap"),
      color = "yellow"
    )
  })


  # Student Count

  output$studentCount <- renderValueBox({

    valueBox(
      nrow(filteredData()),
      "Total Records",
      icon = icon("users"),
      color = "purple"
    )
  })


  # Subject-wise Performance

  output$subjectPlot <- renderPlotly({

    subject_data <- filteredData() %>%
      group_by(Subject) %>%
      summarise(
        Average_Marks = mean(Marks),
        .groups = "drop"
      )

    p <- ggplot(
      subject_data,
      aes(
        x = Subject,
        y = Average_Marks,
        fill = Subject
      )
    ) +
      geom_col() +
      labs(
        x = "Subject",
        y = "Average Marks"
      ) +
      theme_minimal() +
      theme(
        axis.text.x =
          element_text(angle = 30, hjust = 1)
      )

    ggplotly(p)
  })


  # Marks Distribution

  output$marksPlot <- renderPlotly({

    p <- ggplot(
      filteredData(),
      aes(x = Marks)
    ) +
      geom_histogram(
        binwidth = 5,
        fill = "steelblue",
        color = "white"
      ) +
      theme_minimal() +
      labs(
        x = "Marks",
        y = "Number of Students"
      )

    ggplotly(p)
  })


  # Attendance vs Marks

  output$attendancePlot <- renderPlotly({

    p <- ggplot(
      filteredData(),
      aes(
        x = Attendance,
        y = Marks,
        color = Result,
        text = paste(
          "Student:", Name,
          "<br>Marks:", Marks,
          "<br>Attendance:", Attendance
        )
      )
    ) +
      geom_point(size = 3) +
      theme_minimal() +
      labs(
        x = "Attendance (%)",
        y = "Marks"
      )

    ggplotly(
      p,
      tooltip = "text"
    )
  })


  # Grade Distribution

  output$gradePlot <- renderPlotly({

    grade_data <- filteredData() %>%
      count(Grade)

    p <- ggplot(
      grade_data,
      aes(
        x = Grade,
        y = n,
        fill = Grade
      )
    ) +
      geom_col() +
      theme_minimal() +
      labs(
        x = "Grade",
        y = "Number of Students"
      )

    ggplotly(p)
  })


  # Interactive Table

  output$studentTable <- renderDT({

    datatable(
      filteredData(),
      options = list(
        pageLength = 10,
        scrollX = TRUE
      ),
      filter = "top"
    )
  })
}


# ----------------------------
# RUN APPLICATION
# ----------------------------

shinyApp(
  ui = ui,
  server = server
)