package com.restaurant.ai.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.restaurant.ai.dto.OrderItemRequestDTO;
import com.restaurant.ai.dto.OrderRequestDTO;
import com.restaurant.ai.model.*;
import com.restaurant.ai.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.hamcrest.Matchers.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class BackendControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private MenuItemRepository menuItemRepository;

    @MockBean
    private OrderRepository orderRepository;

    @MockBean
    private OrderItemRepository orderItemRepository;

    @MockBean
    private RecipeMasterRepository recipeMasterRepository;

    @MockBean
    private InventoryRepository inventoryRepository;

    @MockBean
    private DemandPredictionRepository demandPredictionRepository;

    @MockBean
    private InventoryPredictionRepository inventoryPredictionRepository;

    private MenuItem burger;
    private MenuItem pizza;

    @BeforeEach
    public void setup() {
        burger = new MenuItem();
        burger.setId(1);
        burger.setItemName("Veggie Burger");
        burger.setCategory("Burgers");
        burger.setPrice(new BigDecimal("5.99"));
        burger.setIsAvailable(true);

        pizza = new MenuItem();
        pizza.setId(2);
        pizza.setItemName("Margherita Pizza");
        pizza.setCategory("Pizza");
        pizza.setPrice(new BigDecimal("8.99"));
        pizza.setIsAvailable(true);
    }

    // ===================== MENU CONTROLLER TESTS =====================

    @Test
    public void testGetAvailableMenuItems() throws Exception {
        Mockito.when(menuItemRepository.findByIsAvailableTrue())
                .thenReturn(List.of(burger, pizza));

        mockMvc.perform(get("/api/menu"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].itemName", is("Veggie Burger")))
                .andExpect(jsonPath("$[1].itemName", is("Margherita Pizza")));
    }

    @Test
    public void testGetAllMenuItems() throws Exception {
        Mockito.when(menuItemRepository.findAll())
                .thenReturn(List.of(burger, pizza));

        mockMvc.perform(get("/api/menu/all"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].itemName", is("Veggie Burger")))
                .andExpect(jsonPath("$[1].itemName", is("Margherita Pizza")));
    }

    @Test
    public void testGetMenuItemsByCategory() throws Exception {
        Mockito.when(menuItemRepository.findByCategory("Burgers"))
                .thenReturn(List.of(burger));

        mockMvc.perform(get("/api/menu/category/Burgers"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].itemName", is("Veggie Burger")));
    }

    @Test
    public void testGetMenuItemById_Found() throws Exception {
        Mockito.when(menuItemRepository.findById(1))
                .thenReturn(Optional.of(burger));

        mockMvc.perform(get("/api/menu/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.itemName", is("Veggie Burger")));
    }

    @Test
    public void testGetMenuItemById_NotFound() throws Exception {
        Mockito.when(menuItemRepository.findById(99))
                .thenReturn(Optional.empty());

        mockMvc.perform(get("/api/menu/99"))
                .andExpect(status().isNotFound());
    }

    // ===================== ORDER CONTROLLER TESTS =====================

    @Test
    public void testCreateOrder_Success() throws Exception {
        // Prepare request
        OrderRequestDTO request = new OrderRequestDTO();
        request.setPaymentMethod("Card");
        request.setPurchaseType("Dine-In");
        request.setCity("San Francisco");
        
        OrderItemRequestDTO itemDTO = new OrderItemRequestDTO();
        itemDTO.setMenuItemId(1);
        itemDTO.setQuantity(2);
        request.setItems(List.of(itemDTO));

        // Mock Menu Item lookup
        Mockito.when(menuItemRepository.findById(1))
                .thenReturn(Optional.of(burger));

        // Mock Recipe lookup (BOM)
        RecipeMaster bunRecipe = new RecipeMaster();
        bunRecipe.setMenuItem(burger);
        bunRecipe.setIngredientName("Burger Bun");
        bunRecipe.setQuantityNeeded(new BigDecimal("1"));
        bunRecipe.setUnit("piece");
        
        Mockito.when(recipeMasterRepository.findByMenuItemId(1))
                .thenReturn(List.of(bunRecipe));

        // Mock Inventory lookup & deduct
        Inventory bunInventory = new Inventory();
        bunInventory.setItemName("Burger Bun");
        bunInventory.setCurrentStock(new BigDecimal("10"));
        
        Mockito.when(inventoryRepository.findTopByItemNameOrderByRecordDateDesc("Burger Bun"))
                .thenReturn(Optional.of(bunInventory));

        // Mock Order save
        Mockito.when(orderRepository.save(any(Order.class)))
                .thenAnswer(invocation -> {
                    Order o = invocation.getArgument(0);
                    o.setId(101);
                    return o;
                });

        mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.orderId", is(101)))
                .andExpect(jsonPath("$.totalAmount", is(11.98))); // 2 * 5.99
    }

    @Test
    public void testCreateOrder_ItemNotFound() throws Exception {
        OrderRequestDTO request = new OrderRequestDTO();
        request.setPaymentMethod("Cash");
        request.setPurchaseType("Takeout");
        
        OrderItemRequestDTO itemDTO = new OrderItemRequestDTO();
        itemDTO.setMenuItemId(99);
        itemDTO.setQuantity(1);
        request.setItems(List.of(itemDTO));

        Mockito.when(menuItemRepository.findById(99))
                .thenReturn(Optional.empty());

        mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success", is(false)))
                .andExpect(jsonPath("$.error", containsString("Menu item not found")));
    }

    @Test
    public void testGetAllOrders() throws Exception {
        Order order = new Order();
        order.setId(1);
        order.setPaymentMethod("Cash");
        order.setPurchaseType("Takeout");
        order.setTotalAmount(new BigDecimal("5.99"));

        Mockito.when(orderRepository.findAllWithItems())
                .thenReturn(List.of(order));

        mockMvc.perform(get("/api/orders"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].id", is(1)))
                .andExpect(jsonPath("$[0].paymentMethod", is("Cash")));
    }

    // ===================== ANALYTICS CONTROLLER TESTS =====================

    @Test
    public void testGetDemandPredictionsByDate() throws Exception {
        LocalDate date = LocalDate.of(2026, 5, 29);
        DemandPrediction pred = new DemandPrediction();
        pred.setId(1);
        pred.setPredictionDate(date);
        pred.setPredictedQuantity(new BigDecimal("25.50"));
        pred.setModelName("XGBoost");

        Mockito.when(demandPredictionRepository.findByPredictionDate(date))
                .thenReturn(List.of(pred));

        mockMvc.perform(get("/api/analytics/demand?date=2026-05-29"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].predictedQuantity", is(25.50)))
                .andExpect(jsonPath("$[0].modelName", is("XGBoost")));
    }

    @Test
    public void testGetInventoryPredictionsByDate() throws Exception {
        LocalDate date = LocalDate.of(2026, 5, 29);
        InventoryPrediction pred = new InventoryPrediction();
        pred.setId(1);
        pred.setInventoryItemName("Tomato");
        pred.setPredictionDate(date);
        pred.setPredictedWastePercentage(new BigDecimal("12.50"));
        pred.setActionRecommended("Reduce Reorder Level");

        Mockito.when(inventoryPredictionRepository.findByPredictionDate(date))
                .thenReturn(List.of(pred));

        mockMvc.perform(get("/api/analytics/inventory?date=2026-05-29"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].inventoryItemName", is("Tomato")))
                .andExpect(jsonPath("$[0].predictedWastePercentage", is(12.50)))
                .andExpect(jsonPath("$[0].actionRecommended", is("Reduce Reorder Level")));
    }
}
