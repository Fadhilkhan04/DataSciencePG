# 1. LOAD REQUIRED LIBRARIES
library(ggplot2)
library(dplyr)
library(lubridate)
library(zoo)

# 2. CREATE THE TIME-SERIES DATASET

# Set seed so the same dataset is generated every time
set.seed(123)

Date <- seq(
  as.Date("2020-01-01"),
  as.Date("2024-12-01"),
  by = "month"
)
# Create month numbers
Month_Number <- month(Date)
# Create year numbers
Year <- year(Date)
# Create a gradual upward trend
Trend <- seq(50000, 90000, length.out = 60)

# Create seasonal pattern
# Higher sales around certain months
Seasonal <- c(
  5000, 3000, 1000, 0, -2000, -4000,
  -3000, -1000, 2000, 5000, 9000, 12000
)

# Repeat seasonal pattern for all 5 years
Seasonal <- rep(Seasonal, 5)

# Random variation
Random_Noise <- rnorm(60, mean = 0, sd = 3000)

# Calculate sales
Sales <- round(Trend + Seasonal + Random_Noise)

# Units sold
Units <- round(Sales / 65 + rnorm(60, 0, 50))

# Advertising expenditure
Advertising <- round(
  Sales * 0.12 + rnorm(60, 0, 1500)
)

# Create final dataset
sales_data <- data.frame(
  Date,
  Sales,
  Units,
  Advertising
)

# Display first few rows
head(sales_data)

# 3. ADD MISSING VALUES AND OUTLIERS

# Add some missing values
sales_data$Sales[c(10, 27, 45)] <- NA

# Add two obvious outliers
sales_data$Sales[c(18, 50)] <- c(150000, 170000)

# Display the modified data
head(sales_data, 20)

# 4. SAVE DATASET AS CSV

write.csv(
  sales_data,
  "sales_data.csv",
  row.names = FALSE
)

cat("CSV file created successfully!\n")


# 5. IMPORT CSV DATASET

sales <- read.csv("sales_data.csv")

head(sales)

# ============================================================
# 6. FIRST AND LAST 10 OBSERVATIONS
# ============================================================

# First 10 observations
head(sales, 10)

# Last 10 observations
tail(sales, 10)


# ============================================================
# 7. EXAMINE DATA STRUCTURE
# ============================================================

str(sales)


# ============================================================
# 8. CONVERT DATE INTO DATE FORMAT
# ============================================================

sales$Date <- as.Date(sales$Date)

str(sales)


# ============================================================
# 9. MINIMUM AND MAXIMUM DATE
# ============================================================

min(sales$Date)

max(sales$Date)


# ============================================================
# 10. CHECK FOR DUPLICATE DATES
# ============================================================

# Number of duplicate dates
sum(duplicated(sales$Date))

# Display duplicate rows if any exist
sales[duplicated(sales$Date), ]


# ============================================================
# 11. CHECK FOR MISSING DATES
# ============================================================

# Create expected monthly dates
expected_dates <- seq(
  min(sales$Date),
  max(sales$Date),
  by = "month"
)

# Compare expected dates with actual dates
missing_dates <- setdiff(
  expected_dates,
  sales$Date
)

missing_dates


# ============================================================
# 12. SUMMARY STATISTICS
# ============================================================

summary(sales)

# Summary of numerical variables
summary(
  sales[, c("Sales", "Units", "Advertising")]
)


# ============================================================
# 13. SELECT VARIABLES
# ============================================================

sales_selected <- sales %>%
  select(Date, Sales)

head(sales_selected)


# ============================================================
# 14. CREATE A NEW VARIABLE
# ============================================================

sales <- sales %>%
  mutate(
    Sales_Lakhs = Sales / 100000
  )

head(sales)


# ============================================================
# 15. FILTER DATA BY YEAR
# ============================================================

sales_2022 <- sales %>%
  filter(
    Date >= as.Date("2022-01-01") &
      Date <= as.Date("2022-12-31")
  )

sales_2022


# ============================================================
# 16. FILTER DATA FROM 2023 ONWARDS
# ============================================================

sales_after_2023 <- sales %>%
  filter(
    Date >= as.Date("2023-01-01")
  )

head(sales_after_2023)


# ============================================================
# 17. CHECK MISSING VALUES
# ============================================================

# Count missing values in each column
colSums(is.na(sales))

# Display rows containing missing values
sales[!complete.cases(sales), ]


# ============================================================
# 18. HANDLE MISSING VALUES - MEAN IMPUTATION
# ============================================================

sales_mean <- sales

sales_mean$Sales[
  is.na(sales_mean$Sales)
] <- mean(
  sales_mean$Sales,
  na.rm = TRUE
)

colSums(is.na(sales_mean))


# ============================================================
# 19. HANDLE MISSING VALUES - MEDIAN IMPUTATION
# ============================================================

sales_median <- sales

sales_median$Sales[
  is.na(sales_median$Sales)
] <- median(
  sales_median$Sales,
  na.rm = TRUE
)

colSums(is.na(sales_median))


# ============================================================
# 20. HANDLE MISSING VALUES - LINEAR INTERPOLATION
# ============================================================

sales_linear <- sales

sales_linear$Sales <- na.approx(
  sales_linear$Sales
)

colSums(is.na(sales_linear))


# ============================================================
# 21. DETECT OUTLIERS USING BOX PLOT
# ============================================================

boxplot(
  sales$Sales,
  main = "Box Plot of Monthly Sales",
  ylab = "Sales"
)


# ============================================================
# 22. DETECT OUTLIERS USING Z-SCORE
# ============================================================

# Calculate Z-scores
z_scores <- scale(sales$Sales)

# Display observations where absolute Z-score > 3
outliers <- sales[
  abs(z_scores) > 3,
]

outliers


# ============================================================
# 23. REMOVE OUTLIERS
# ============================================================

sales_clean <- sales[
  abs(z_scores) <= 3 |
    is.na(z_scores),
]

head(sales_clean)


# ============================================================
# 24. TIME-SERIES VISUALIZATION
# ============================================================

ggplot(
  sales,
  aes(
    x = Date,
    y = Sales
  )
) +
  geom_line(na.rm = TRUE) +
  labs(
    title = "Monthly Sales Over Time",
    x = "Date",
    y = "Sales"
  ) +
  theme_minimal()

# ============================================================
# 27. CALCULATE 3-MONTH MOVING AVERAGE
# ============================================================

sales$Moving_Average <- rollmean(
  sales$Sales,
  k = 3,
  fill = NA,
  align = "right",
  na.rm = FALSE
)

head(sales, 10)


# ============================================================
# 28. PLOT SALES WITH MOVING AVERAGE
# ============================================================

ggplot(
  sales,
  aes(x = Date)
) +
  geom_line(
    aes(y = Sales),
    na.rm = TRUE
  ) +
  geom_line(
    aes(y = Moving_Average),
    linewidth = 1,
    na.rm = TRUE
  ) +
  labs(
    title = "Monthly Sales and 3-Month Moving Average",
    x = "Date",
    y = "Sales"
  ) +
  theme_minimal()


# ============================================================
# 29. IDENTIFY MONTHLY SEASONALITY
# ============================================================

# Extract month
sales$Month <- month(
  sales$Date,
  label = TRUE
)

# Calculate average sales for each month
monthly_sales <- sales %>%
  group_by(Month) %>%
  summarise(
    Average_Sales = mean(
      Sales,
      na.rm = TRUE
    )
  )

monthly_sales


# ============================================================
# 30. HIGHEST SALES MONTH
# ============================================================

highest_month <- monthly_sales %>%
  arrange(
    desc(Average_Sales)
  ) %>%
  head(1)

highest_month


# ============================================================
# 31. LOWEST SALES MONTH
# ============================================================

lowest_month <- monthly_sales %>%
  arrange(
    Average_Sales
  ) %>%
  head(1)

lowest_month


# ============================================================
# 32. SEASONALITY GRAPH
# ============================================================

ggplot(
  monthly_sales,
  aes(
    x = Month,
    y = Average_Sales,
    group = 1
  )
) +
  geom_line() +
  geom_point() +
  labs(
    title = "Monthly Seasonal Sales Pattern",
    x = "Month",
    y = "Average Sales"
  ) +
  theme_minimal()


# ============================================================
# 33. FINAL SEASONAL ANALYSIS
# ============================================================

seasonal_summary <- sales %>%
  group_by(Month) %>%
  summarise(
    Average = mean(
      Sales,
      na.rm = TRUE
    ),
    Maximum = max(
      Sales,
      na.rm = TRUE
    ),
    Minimum = min(
      Sales,
      na.rm = TRUE
    )
  )

seasonal_summary


# ============================================================
# END OF LAB
# ============================================================

cat("Time Series Analysis Lab Completed Successfully!\n")