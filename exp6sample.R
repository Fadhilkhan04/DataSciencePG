# 1. Load libraries
library(ggplot2)
library(dplyr)
library(lubridate)
library(zoo)

# 2. Create dataset
set.seed(123)

Date <- seq(as.Date("2020-01-01"),
            as.Date("2024-12-01"), by = "month")

Sales <- round(seq(50000, 90000, length.out = 60) +
               rnorm(60, 0, 3000))

sales <- data.frame(
  Date = Date,
  Sales = Sales,
  Units = round(Sales / 65),
  Advertising = round(Sales * 0.12)
)

# Add missing values and outliers
sales$Sales[c(10, 27, 45)] <- NA
sales$Sales[c(18, 50)] <- c(150000, 170000)

# 3. Save and import CSV
write.csv(sales, "sales_data.csv", row.names = FALSE)
sales <- read.csv("sales_data.csv")
sales$Date <- as.Date(sales$Date)

# 4. Examine dataset
print(head(sales))
print(tail(sales))
str(sales)
summary(sales)

# 5. Check dates and missing values
print(range(sales$Date))
print(sum(duplicated(sales$Date)))
print(colSums(is.na(sales)))

# 6. Select columns and filter data
sales_selected <- sales %>% select(Date, Sales)

sales_2022 <- sales %>%
  filter(year(Date) == 2022)

print(sales_2022)

# 7. Handle missing values using interpolation
sales$Sales <- na.approx(sales$Sales, na.rm = FALSE)
sales$Sales <- na.locf(sales$Sales, na.rm = FALSE)
sales$Sales <- na.locf(sales$Sales, fromLast = TRUE)

# 8. Detect outliers using boxplot
boxplot(sales$Sales, main = "Sales Outliers")

z <- as.numeric(scale(sales$Sales))
print(sales[abs(z) > 3, ])

# Remove outliers
sales_clean <- sales[abs(z) <= 3, ]

# 9. Calculate moving average
sales$Moving_Average <- rollmean(
  sales$Sales, k = 3, fill = NA, align = "right"
)

# 10. Plot sales and moving average
ggplot(sales, aes(x = Date)) +
  geom_line(aes(y = Sales), na.rm = TRUE) +
  geom_line(aes(y = Moving_Average), na.rm = TRUE,
            color = "red") +
  labs(title = "Monthly Sales and Moving Average",
       x = "Date", y = "Sales") +
  theme_minimal()

# 11. Monthly seasonal analysis
sales$Month <- month(sales$Date, label = TRUE)

monthly_sales <- sales %>%
  group_by(Month) %>%
  summarise(Average_Sales = mean(Sales, na.rm = TRUE))

print(monthly_sales)

# Highest and lowest sales months
print(monthly_sales %>% slice_max(Average_Sales, n = 1))
print(monthly_sales %>% slice_min(Average_Sales, n = 1))

# 12. Seasonal graph
ggplot(monthly_sales, aes(x = Month, y = Average_Sales,
                          group = 1)) +
  geom_line() +
  geom_point() +
  labs(title = "Monthly Seasonal Sales Pattern",
       x = "Month", y = "Average Sales") +
  theme_minimal()

cat("Time Series Analysis Completed Successfully!")