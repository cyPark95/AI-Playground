package pcy.study.aiplayground.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pcy.study.aiplayground.service.ProductService;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductController {

    private final ProductService productService;

    @PostMapping("/{id}/order")
    @ResponseStatus(HttpStatus.CREATED)
    public void order(@PathVariable Long id, @RequestParam int quantity) {
        productService.orderProduct(id, quantity);
    }

    @GetMapping("/total-stock")
    public long getTotalStock() {
        return productService.getTotalStockValue();
    }
}
