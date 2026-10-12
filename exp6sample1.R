# 1. Load libraries
library(ggplot2)
library(dplyr)
library(lubridate)
library(zoo)

# 2. Import dataset
sales <- read.csv("sales_data.csv")

# 3. Examine dataset
print(head(sales))
print(tail(sales))
str(sales)
summary(sales)

# 4. Convert Date column
sales$Date <- as.Date(sales$Date)

# 5. Check dates and duplicates
print(range(sales$Date))
print(sum(duplicated(sales$Date)))

# 6. Check missing values
print(colSums(is.na(sales)))

# 7. Select columns
sales_selected <- sales %>%
  select(Date, Sales)

# 8. Filter data for 2022
sales_2022 <- sales %>%
  filter(year(Date) == 2022)

print(sales_2022)

# 9. Create a new variable
sales <- sales %>%
  mutate(Sales_Lakhs = Sales / 100000)

# 10. Handle missing values using interpolation
sales$Sales <- na.approx(sales$Sales, na.rm = FALSE)
sales$Sales <- na.locf(sales$Sales, na.rm = FALSE)
sales$Sales <- na.locf(sales$Sales, fromLast = TRUE)

# 11. Detect outliers using boxplot
boxplot(sales$Sales, main = "Sales Boxplot")

# 12. Detect and remove outliers using Z-score
z <- as.numeric(scale(sales$Sales))
outliers <- sales[abs(z) > 3, ]
print(outliers)

sales_clean <- sales[abs(z) <= 3, ]

# 13. Plot monthly sales
ggplot(sales, aes(x = Date, y = Sales)) +
  geom_line(na.rm = TRUE) +
  labs(title = "Monthly Sales Over Time",
       x = "Date", y = "Sales") +
  theme_minimal()

# 14. Calculate 3-month moving average
sales$Moving_Average <- rollmean(
  sales$Sales, k = 3, fill = NA, align = "right"
)

# 15. Plot sales and moving average
ggplot(sales, aes(x = Date)) +
  geom_line(aes(y = Sales), na.rm = TRUE) +
  geom_line(aes(y = Moving_Average), na.rm = TRUE) +
  labs(title = "Sales and Moving Average",
       x = "Date", y = "Sales") +
  theme_minimal()

# 16. Monthly seasonal analysis
sales$Month <- month(sales$Date, label = TRUE)

monthly_sales <- sales %>%
  group_by(Month) %>%
  summarise(Average_Sales = mean(Sales, na.rm = TRUE))

print(monthly_sales)

# 17. Highest and lowest sales months
print(slice_max(monthly_sales, Average_Sales, n = 1))
print(slice_min(monthly_sales, Average_Sales, n = 1))

# 18. Plot seasonal pattern
ggplot(monthly_sales,
       aes(x = Month, y = Average_Sales, group = 1)) +
  geom_line() +
  geom_point() +
  labs(title = "Monthly Seasonal Sales Pattern",
       x = "Month", y = "Average Sales") +
  theme_minimal()

cat("Data Processing Completed Successfully!")