package com.restaurant.ai.model;

import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

/**
 * JPA Entity mapped to the 'orders' table.
 * Represents a customer order/bill in the Smart Billing System.
 */
@Entity
@Table(name = "orders")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "order_date", nullable = false)
    private LocalDate orderDate;

    @Column(name = "order_time")
    private LocalTime orderTime;

    @Column(name = "time_of_sale", length = 20)
    private String timeOfSale;

    @Column(name = "total_amount", nullable = false, precision = 12, scale = 2)
    private BigDecimal totalAmount = BigDecimal.ZERO;

    @Column(name = "payment_method", length = 30)
    private String paymentMethod;

    @Column(name = "purchase_type", length = 30)
    private String purchaseType;

    @Column(name = "cashier_id")
    private Integer cashierId;

    @Column(name = "manager_name", length = 100)
    private String managerName;

    @Column(length = 50)
    private String city;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference
    private List<OrderItem> orderItems = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (orderDate == null) {
            orderDate = LocalDate.now();
        }
        if (orderTime == null) {
            orderTime = LocalTime.now();
        }
        if (timeOfSale == null) {
            int hour = orderTime.getHour();
            if (hour >= 6 && hour < 12) timeOfSale = "Morning";
            else if (hour >= 12 && hour < 17) timeOfSale = "Afternoon";
            else if (hour >= 17 && hour < 21) timeOfSale = "Evening";
            else if (hour >= 21 && hour < 24) timeOfSale = "Night";
            else timeOfSale = "Midnight";
        }
    }
}
