package pcy.study.aiplayground.controller;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import pcy.study.aiplayground.service.ProductService;

import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;

    @Test
    @DisplayName("주문 API 호출 시 201 Created를 반환해야 한다.")
    void order_ReturnsCreated() throws Exception {
        // given
        Long productId = 1L;
        int quantity = 5;
        doNothing().when(productService).orderProduct(productId, quantity);

        // when & then
        mockMvc.perform(post("/api/products/{id}/order", productId)
                        .param("quantity", String.valueOf(quantity)))
                .andExpect(status().isCreated());
    }

    @Test
    @DisplayName("전체 재고 조회 API는 총 재고량을 반환해야 한다.")
    void getTotalStock_ReturnsValue() throws Exception {
        // given
        when(productService.getTotalStockValue()).thenReturn(150L);

        // when & then
        mockMvc.perform(get("/api/products/total-stock"))
                .andExpect(status().isOk())
                .andExpect(content().string("150"));
    }
}
