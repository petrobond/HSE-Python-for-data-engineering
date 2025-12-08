# Скрипт для анализа продаж
# Формат файла: дата день_недели товар цена количество

SALES_FILE="sales.txt"

# Проверяем существование файла
if [ ! -f "$SALES_FILE" ]; then
    echo "Ошибка: файл $SALES_FILE не найден"
    exit 1
fi

# 1. Подсчет общей суммы продаж
total_sum=$(awk '{sum += $4 * $5} END {printf "%.2f", sum}' "$SALES_FILE")
echo "Общая сумма продаж: $total_sum"

# 2. Дата и день недели с наибольшей суммой продаж
best_day=$(awk '{
    key = $1 " " $2
    sales[key] += $4 * $5
}
END {
    max_sum = 0
    max_key = ""
    for (key in sales) {
        if (sales[key] > max_sum) {
            max_sum = sales[key]
            max_key = key
        }
    }
    printf "%s (сумма продаж: %.0f)", max_key, max_sum
}' "$SALES_FILE")
echo "День с наибольшей выручкой: $best_day"

# 3. Самый популярный товар (по количеству проданных единиц)
popular_product=$(awk '{
    qty[tolower($3)] += $5
    revenue[tolower($3)] += $4 * $5
}
END {
    max_qty = 0
    max_product = ""
    for (product in qty) {
        if (qty[product] > max_qty) {
            max_qty = qty[product]
            max_product = product
        }
    }
    printf "%s (количество проданных единиц: %d, сумма продаж: %.0f)", max_product, max_qty, revenue[max_product]
}' "$SALES_FILE")
echo "Популярный товар: $popular_product"

