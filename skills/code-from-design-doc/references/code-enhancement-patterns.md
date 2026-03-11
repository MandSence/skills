# 代码增强模式参考指南

本文档提供了代码增强模式的详细实现模板和最佳实践，供技能执行时参考使用。

## 目录

- [1. 后端增强模式](#1-后端增强模式)
  - [1.1 多级缓存模式](#11-多级缓存模式)
  - [1.2 分页排序模式](#12-分页排序模式)
  - [1.3 状态机模式](#13-状态机模式)
  - [1.4 策略模式](#14-策略模式)
  - [1.5 熔断降级模式](#15-熔断降级模式)
  - [1.6 限流保护模式](#16-限流保护模式)
- [2. 前端增强模式](#2-前端增强模式)
  - [2.1 防抖节流模式](#21-防抖节流模式)
  - [2.2 乐观更新模式](#22-乐观更新模式)
  - [2.3 请求重试模式](#23-请求重试模式)
  - [2.4 骨架屏模式](#24-骨架屏模式)
  - [2.5 错误边界模式](#25-错误边界模式)
- [3. 算法选择决策树](#3-算法选择决策树)
- [4. 性能优化最佳实践](#4-性能优化最佳实践)
- [5. 缓存策略](#5-缓存策略)
- [6. 错误处理规范](#6-错误处理规范)

---

## 1. 后端增强模式

### 1.1 多级缓存模式

**适用场景**：高频读取的数据，如用户信息、组织列表、配置数据

**实现模板（TypeScript）**：
```typescript
import { LRUCache } from 'lru-cache';
import { Redis } from 'ioredis';

// L1缓存：进程内存缓存（LRU）
const l1Cache = new LRUCache<string, any>({
    max: 1000,           // 最大缓存条目
    ttl: 60 * 1000,      // 1分钟过期
});

// L2缓存：Redis
const redis = new Redis();

// L3：数据库
class UserRepository {
    /**
     * 多级缓存查询
     * @param key 缓存键
     * @param dbQuery 数据库查询函数
     * @param options 配置选项
     */
    async getWithCache<T>(
        key: string,
        dbQuery: () => Promise<T>,
        options: {
            l1Ttl?: number;    // L1缓存TTL（秒）
            l2Ttl?: number;    // L2缓存TTL（秒）
            forceRefresh?: boolean; // 强制刷新缓存
        } = {}
    ): Promise<T> {
        const { l1Ttl = 60, l2Ttl = 300, forceRefresh = false } = options;

        // 1. 检查L1缓存
        if (!forceRefresh) {
            const l1Data = l1Cache.get(key);
            if (l1Data) {
                console.log(`[Cache] L1 Hit: ${key}`);
                return l1Data;
            }
        }

        // 2. 检查L2缓存（Redis）
        if (!forceRefresh) {
            const l2Data = await redis.get(key);
            if (l2Data) {
                console.log(`[Cache] L2 Hit: ${key}`);
                const parsed = JSON.parse(l2Data);
                // 回写L1缓存
                l1Cache.set(key, parsed, { ttl: l1Ttl * 1000 });
                return parsed;
            }
        }

        // 3. 查询数据库
        console.log(`[Cache] Cache Miss, Querying DB: ${key}`);
        const data = await dbQuery();

        // 4. 写入缓存
        l1Cache.set(key, data, { ttl: l1Ttl * 1000 });
        await redis.setex(key, l2Ttl, JSON.stringify(data));

        return data;
    }

    /**
     * 清除指定缓存
     */
    async invalidateCache(pattern: string): Promise<void> {
        l1Cache.delete(pattern);
        const keys = await redis.keys(pattern);
        if (keys.length > 0) {
            await redis.del(...keys);
        }
    }

    /**
     * 缓存预热
     */
    async warmup(keys: string[]): Promise<void> {
        for (const key of keys) {
            await this.getWithCache(key, async () => {
                return this.findByKey(key);
            });
        }
    }
}

// 使用示例
const userRepo = new UserRepository();

async function getUser(id: string) {
    return userRepo.getWithCache(
        `user:${id}`,
        () => userRepo.findById(id),
        { l1Ttl: 30, l2Ttl: 300 }
    );
}

// 用户更新后清除缓存
async function updateUser(id: string, data: any) {
    await userRepo.update(id, data);
    await userRepo.invalidateCache(`user:${id}`);
}
```

---

### 1.2 分页排序模式

**适用场景**：列表查询、数据展示

**实现模板（TypeScript）**：
```typescript
interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
}

interface PaginationResult<T> {
    data: T[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
    hasMore: boolean;
}

class BaseRepository<T> {
    /**
     * 分页查询（偏移分页）
     */
    async paginate(
        query: any,
        options: PaginationOptions
    ): Promise<PaginationResult<T>> {
        const { page, pageSize, sortBy = 'createdAt', sortOrder = 'desc' } = options;
        const skip = (page - 1) * pageSize;
        const take = pageSize;

        const [data, total] = await Promise.all([
            this.find(query)
                .skip(skip)
                .take(take)
                .orderBy({ [sortBy]: sortOrder }),
            this.count(query)
        ]);

        return {
            data,
            total,
            page,
            pageSize,
            totalPages: Math.ceil(total / pageSize),
            hasMore: skip + take < total
        };
    }

    /**
     * 游标分页（用于无限滚动）
     */
    async paginateByCursor(
        query: any,
        options: {
            cursor?: string;
            pageSize: number;
            sortBy?: string;
            sortOrder?: 'asc' | 'desc';
        }
    ): Promise<{ data: T[]; nextCursor: string | null }> {
        const { cursor, pageSize, sortBy = 'id', sortOrder = 'asc' } = options;

        let queryBuilder = this.find(query).take(pageSize + 1);

        if (cursor) {
            const cursorValue = Buffer.from(cursor, 'base64').toString();
            queryBuilder = queryBuilder.where({
                [sortBy]: sortOrder === 'asc'
                    ? { gt: cursorValue }
                    : { lt: cursorValue }
            });
        }

        queryBuilder = queryBuilder.orderBy({ [sortBy]: sortOrder });

        const data = await queryBuilder.execute();
        const hasNext = data.length > pageSize;
        const items = data.slice(0, pageSize);
        const nextCursor = hasNext
            ? Buffer.from(items[items.length - 1][sortBy]).toString('base64')
            : null;

        return { data: items, nextCursor };
    }

    /**
     * 批量查询（解决N+1问题）
     */
    async findByIdsWithRelations(
        ids: string[],
        relations: string[]
    ): Promise<Map<string, T>> {
        const items = await this.find({ id: { in: ids } })
            .with(relations)
            .execute();

        const resultMap = new Map<string, T>();
        items.forEach(item => resultMap.set(item.id, item));

        return resultMap;
    }
}

// 使用示例
const repo = new BaseRepository<Order>();

// 偏移分页
const result = await repo.paginate(
    { userId: '123' },
    { page: 1, pageSize: 20, sortBy: 'createdAt', sortOrder: 'desc' }
);

// 游标分页
const { data, nextCursor } = await repo.paginateByCursor(
    { userId: '123' },
    { cursor: '...', pageSize: 20, sortBy: 'createdAt', sortOrder: 'desc' }
);

// 批量查询
const orderMap = await repo.findByIdsWithRelations(
    ['order1', 'order2', 'order3'],
    ['items', 'user']
);
```

---

### 1.3 状态机模式

**适用场景**：订单状态、工单状态、审批流程等

**实现模板（TypeScript）**：
```typescript
/**
 * 状态机模式实现
 */
enum State {
    PENDING = 'PENDING',
    APPROVED = 'APPROVED',
    REJECTED = 'REJECTED',
    COMPLETED = 'COMPLETED',
    CANCELLED = 'CANCELLED'
}

type Event =
    | { type: 'APPROVE'; userId: string; reason?: string }
    | { type: 'REJECT'; userId: string; reason: string }
    | { type: 'COMPLETE'; userId: string }
    | { type: 'CANCEL'; userId: string; reason: string };

interface StateTransition {
    from: State;
    to: State;
    event: Event['type'];
}

// 状态转换规则
const TRANSITIONS: Record<State, StateTransition[]> = {
    [State.PENDING]: [
        { from: State.PENDING, to: State.APPROVED, event: 'APPROVE' },
        { from: State.PENDING, to: State.REJECTED, event: 'REJECT' },
        { from: State.PENDING, to: State.CANCELLED, event: 'CANCEL' }
    ],
    [State.APPROVED]: [
        { from: State.APPROVED, to: State.COMPLETED, event: 'COMPLETE' },
        { from: State.APPROVED, to: State.CANCELLED, event: 'CANCEL' }
    ],
    [State.REJECTED]: [
        { from: State.REJECTED, to: State.CANCELLED, event: 'CANCEL' }
    ],
    [State.COMPLETED]: [],
    [State.CANCELLED]: []
};

interface StateHistory {
    state: State;
    previousState: State | null;
    event: Event['type'];
    userId: string;
    reason?: string;
    timestamp: Date;
}

class StateMachine {
    private currentState: State;
    private history: StateHistory[] = [];

    constructor(initialState: State = State.PENDING) {
        this.currentState = initialState;
        this.recordHistory(null, 'INITIAL', 'system');
    }

    /**
     * 获取当前状态
     */
    getState(): State {
        return this.currentState;
    }

    /**
     * 获取可转换的目标状态
     */
    getAllowedTransitions(): State[] {
        return TRANSITIONS[this.currentState]?.map(t => t.to) ?? [];
    }

    /**
     * 检查是否可以转换到目标状态
     */
    canTransition(to: State): boolean {
        return this.getAllowedTransitions().includes(to);
    }

    /**
     * 执行状态转换
     */
    async transition(event: Event): Promise<void> {
        const { type, userId, reason } = event;

        // 查找对应的转换规则
        const transition = TRANSITIONS[this.currentState]?.find(t => t.event === type);

        if (!transition) {
            throw new Error(
                `Invalid transition: ${this.currentState} --[${type}]--> ?`
            );
        }

        // 执行退出钩子
        await this.onExit(this.currentState, event);

        // 更新状态
        const previousState = this.currentState;
        this.currentState = transition.to;

        // 记录历史
        this.recordHistory(previousState, type, userId, reason);

        // 执行进入钩子
        await this.onEnter(transition.to, event);

        console.log(`[StateMachine] ${previousState} --> ${this.currentState}`);
    }

    /**
     * 状态退出钩子
     */
    private async onExit(state: State, event: Event): Promise<void> {
        switch (state) {
            case State.PENDING:
                await this.cancelTimeoutTask();
                break;
            case State.APPROVED:
                // 发送取消通知
                break;
        }
    }

    /**
     * 状态进入钩子
     */
    private async onEnter(state: State, event: Event): Promise<void> {
        switch (state) {
            case State.APPROVED:
                await this.sendApprovalNotification(event);
                await this.scheduleCompletionReminder();
                break;
            case State.REJECTED:
                await this.sendRejectionNotification(event);
                break;
            case State.COMPLETED:
                await this.sendCompletionNotification(event);
                await this.updateStatistics();
                break;
            case State.CANCELLED:
                await this.sendCancellationNotification(event);
                await this.rollbackResources();
                break;
        }
    }

    /**
     * 获取状态历史
     */
    getHistory(): StateHistory[] {
        return [...this.history];
    }

    private recordHistory(
        previousState: State | null,
        event: Event['type'],
        userId: string,
        reason?: string
    ): void {
        this.history.push({
            state: this.currentState,
            previousState,
            event,
            userId,
            reason,
            timestamp: new Date()
        });
    }

    private async cancelTimeoutTask(): Promise<void> {}
    private async scheduleCompletionReminder(): Promise<void> {}
    private async sendApprovalNotification(event: Event): Promise<void> {}
    private async sendRejectionNotification(event: Event): Promise<void> {}
    private async sendCompletionNotification(event: Event): Promise<void> {}
    private async sendCancellationNotification(event: Event): Promise<void> {}
    private async updateStatistics(): Promise<void> {}
    private async rollbackResources(): Promise<void> {}
}

// 使用示例
const fsm = new StateMachine(State.PENDING);

await fsm.transition({ type: 'APPROVE', userId: 'user1', reason: '符合条件' });
console.log(fsm.getState()); // State.APPROVED

await fsm.transition({ type: 'COMPLETE', userId: 'user1' });
console.log(fsm.getState()); // State.COMPLETED

console.log(fsm.getHistory());
```

---

### 1.4 策略模式

**适用场景**：多种支付方式、多种通知方式、多种验证规则

**实现模板（TypeScript）**：
```typescript
/**
 * 支付策略模式
 */

// 支付结果接口
interface PaymentResult {
    success: boolean;
    transactionId?: string;
    errorCode?: string;
    errorMessage?: string;
    rawResponse?: any;
}

// 支付策略接口
interface PaymentStrategy {
    name: string;
    pay(amount: number, order: Order): Promise<PaymentResult>;
    refund(transactionId: string, amount: number): Promise<PaymentResult>;
    query(transactionId: string): Promise<PaymentResult>;
}

// 订单实体
interface Order {
    id: string;
    amount: number;
    userId: string;
}

// 微信支付策略
class WechatPayStrategy implements PaymentStrategy {
    name = 'wechat';

    async pay(amount: number, order: Order): Promise<PaymentResult> {
        try {
            const response = await this.callWechatAPI({
                outTradeNo: order.id,
                totalFee: amount * 100, // 分
                openid: order.userId
            });

            if (response.returnCode === 'SUCCESS') {
                return {
                    success: true,
                    transactionId: response.transactionId,
                    rawResponse: response
                };
            } else {
                return {
                    success: false,
                    errorCode: response.errCode,
                    errorMessage: response.errMsg,
                    rawResponse: response
                };
            }
        } catch (error) {
            return {
                success: false,
                errorCode: 'NETWORK_ERROR',
                errorMessage: error.message
            };
        }
    }

    async refund(transactionId: string, amount: number): Promise<PaymentResult> {
        const response = await this.callRefundAPI({
            transactionId,
            refundFee: amount * 100
        });

        return {
            success: response.returnCode === 'SUCCESS',
            transactionId: response.refundId
        };
    }

    async query(transactionId: string): Promise<PaymentResult> {
        const response = await this.callQueryAPI({ transactionId });
        return {
            success: response.tradeState === 'SUCCESS',
            rawResponse: response
        };
    }

    private async callWechatAPI(params: any): Promise<any> {
        // 实际调用微信支付API
        return {};
    }

    private async callRefundAPI(params: any): Promise<any> {
        // 实际调用微信退款API
        return {};
    }

    private async callQueryAPI(params: any): Promise<any> {
        // 实际调用微信查询API
        return {};
    }
}

// 支付宝支付策略
class AlipayStrategy implements PaymentStrategy {
    name = 'alipay';

    async pay(amount: number, order: Order): Promise<PaymentResult> {
        try {
            const response = await this.callAlipayAPI({
                outTradeNo: order.id,
                totalAmount: amount.toFixed(2),
                buyerId: order.userId
            });

            return {
                success: response.code === '10000',
                transactionId: response.tradeNo,
                rawResponse: response
            };
        } catch (error) {
            return {
                success: false,
                errorCode: 'NETWORK_ERROR',
                errorMessage: error.message
            };
        }
    }

    async refund(transactionId: string, amount: number): Promise<PaymentResult> {
        const response = await this.callRefundAPI({
            tradeNo: transactionId,
            refundAmount: amount.toFixed(2)
        });

        return {
            success: response.code === '10000',
            transactionId: response.outRequestNo
        };
    }

    async query(transactionId: string): Promise<PaymentResult> {
        const response = await this.callQueryAPI({ tradeNo: transactionId });
        return {
            success: response.tradeStatus === 'TRADE_SUCCESS',
            rawResponse: response
        };
    }

    private async callAlipayAPI(params: any): Promise<any> {
        // 实际调用支付宝API
        return {};
    }

    private async callRefundAPI(params: any): Promise<any> {
        // 实际调用支付宝退款API
        return {};
    }

    private async callQueryAPI(params: any): Promise<any> {
        // 实际调用支付宝查询API
        return {};
    }
}

// 支付上下文（策略工厂）
class PaymentContext {
    private strategies: Map<string, PaymentStrategy> = new Map();

    register(strategy: PaymentStrategy): void {
        this.strategies.set(strategy.name, strategy);
    }

    getStrategy(name: string): PaymentStrategy {
        const strategy = this.strategies.get(name);
        if (!strategy) {
            throw new Error(`Payment strategy '${name}' not found`);
        }
        return strategy;
    }

    async pay(
        strategyName: string,
        amount: number,
        order: Order
    ): Promise<PaymentResult> {
        const strategy = this.getStrategy(strategyName);
        return strategy.pay(amount, order);
    }

    async refund(
        strategyName: string,
        transactionId: string,
        amount: number
    ): Promise<PaymentResult> {
        const strategy = this.getStrategy(strategyName);
        return strategy.refund(transactionId, amount);
    }
}

// 使用示例
const paymentContext = new PaymentContext();
paymentContext.register(new WechatPayStrategy());
paymentContext.register(new AlipayStrategy());

// 使用微信支付
const result1 = await paymentContext.pay('wechat', 100, {
    id: 'order1',
    amount: 100,
    userId: 'user1'
});

// 使用支付宝支付
const result2 = await paymentContext.pay('alipay', 100, {
    id: 'order2',
    amount: 100,
    userId: 'user2'
});
```

---

### 1.5 熔断降级模式

**适用场景**：外部API调用、第三方服务集成

**实现模板（TypeScript）**：
```typescript
/**
 * 熔断器模式
 */
enum CircuitState {
    CLOSED = 'CLOSED',      // 关闭：正常工作
    OPEN = 'OPEN',          // 开启：熔断状态
    HALF_OPEN = 'HALF_OPEN' // 半开启：尝试恢复
}

interface CircuitBreakerOptions {
    failureThreshold: number;    // 失败阈值
    successThreshold: number;    // 成功阈值（半开启状态）
    timeout: number;            // 熔断超时时间（毫秒）
    monitoringPeriod: number;    // 监控周期（毫秒）
}

class CircuitBreaker {
    private state: CircuitState = CircuitState.CLOSED;
    private failureCount = 0;
    private successCount = 0;
    private lastFailureTime = 0;
    private options: CircuitBreakerOptions;

    constructor(options: Partial<CircuitBreakerOptions> = {}) {
        this.options = {
            failureThreshold: options.failureThreshold ?? 5,
            successThreshold: options.successThreshold ?? 2,
            timeout: options.timeout ?? 60000,
            monitoringPeriod: options.monitoringPeriod ?? 10000
        };
    }

    /**
     * 执行受保护的函数
     */
    async execute<T>(fn: () => Promise<T>, fallback?: () => T): Promise<T> {
        // 检查是否处于熔断状态
        if (this.state === CircuitState.OPEN) {
            if (this.shouldAttemptReset()) {
                this.state = CircuitState.HALF_OPEN;
                this.successCount = 0;
            } else {
                throw new CircuitBreakerOpenError('Circuit breaker is OPEN');
            }
        }

        try {
            const result = await fn();
            this.onSuccess();
            return result;
        } catch (error) {
            this.onFailure();
            if (fallback) {
                return fallback();
            }
            throw error;
        }
    }

    /**
     * 成功处理
     */
    private onSuccess(): void {
        this.failureCount = 0;

        if (this.state === CircuitState.HALF_OPEN) {
            this.successCount++;
            if (this.successCount >= this.options.successThreshold) {
                this.state = CircuitState.CLOSED;
                console.log('[CircuitBreaker] Circuit CLOSED');
            }
        }
    }

    /**
     * 失败处理
     */
    private onFailure(): void {
        this.failureCount++;
        this.lastFailureTime = Date.now();

        if (this.failureCount >= this.options.failureThreshold) {
            this.state = CircuitState.OPEN;
            console.log('[CircuitBreaker] Circuit OPEN');
        }
    }

    /**
     * 检查是否尝试重置熔断器
     */
    private shouldAttemptReset(): boolean {
        const timeSinceLastFailure = Date.now() - this.lastFailureTime;
        return timeSinceLastFailure > this.options.timeout;
    }

    /**
     * 获取当前状态
     */
    getState(): CircuitState {
        return this.state;
    }

    /**
     * 重置熔断器
     */
    reset(): void {
        this.state = CircuitState.CLOSED;
        this.failureCount = 0;
        this.successCount = 0;
    }
}

class CircuitBreakerOpenError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'CircuitBreakerOpenError';
    }
}

// 熔断器管理器
class CircuitBreakerRegistry {
    private breakers = new Map<string, CircuitBreaker>();

    get(key: string): CircuitBreaker {
        if (!this.breakers.has(key)) {
            this.breakers.set(key, new CircuitBreaker());
        }
        return this.breakers.get(key)!;
    }

    reset(key: string): void {
        const breaker = this.breakers.get(key);
        if (breaker) {
            breaker.reset();
        }
    }
}

// 使用示例
const registry = new CircuitBreakerRegistry();

async function callExternalAPI(url: string) {
    const breaker = registry.get('external-api');

    return breaker.execute(
        async () => {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        },
        () => {
            // 降级逻辑：返回缓存数据或默认值
            console.log('[CircuitBreaker] Using fallback data');
            return { status: 'degraded', data: {} };
        }
    );
}
```

---

### 1.6 限流保护模式

**适用场景**：API端点保护、防止暴力攻击

**实现模板（TypeScript）**：
```typescript
/**
 * 限流器（滑动窗口算法）
 */
class RateLimiter {
    private windows = new Map<string, number[]>();
    private windowSize: number;  // 窗口大小（毫秒）
    private maxRequests: number;  // 最大请求数

    constructor(windowSize: number = 60000, maxRequests: number = 100) {
        this.windowSize = windowSize;
        this.maxRequests = maxRequests;
    }

    /**
     * 检查是否允许请求
     */
    async check(key: string): Promise<boolean> {
        const now = Date.now();
        const windowStart = now - this.windowSize;

        // 获取或创建窗口
        let requests = this.windows.get(key) || [];

        // 移除窗口外的请求
        requests = requests.filter(time => time > windowStart);

        // 检查是否超过限制
        if (requests.length >= this.maxRequests) {
            return false;
        }

        // 添加当前请求
        requests.push(now);
        this.windows.set(key, requests);

        return true;
    }

    /**
     * 获取剩余请求次数
     */
    getRemaining(key: string): number {
        const now = Date.now();
        const windowStart = now - this.windowSize;
        const requests = this.windows.get(key) || [];
        const validRequests = requests.filter(time => time > windowStart);
        return Math.max(0, this.maxRequests - validRequests.length);
    }

    /**
     * 获取重置时间
     */
    getResetTime(key: string): number {
        const now = Date.now();
        const windowStart = now - this.windowSize;
        const requests = this.windows.get(key) || [];
        const oldestValidRequest = requests.find(time => time > windowStart);
        return oldestValidRequest ? oldestValidRequest + this.windowSize : now;
    }
}

/**
 * 令牌桶限流器
 */
class TokenBucket {
    private tokens: number;
    private lastRefill = Date.now();
    private capacity: number;
    private refillRate: number;  // 每毫秒补充的令牌数

    constructor(capacity: number = 100, refillRate: number = 1) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = capacity;
    }

    /**
     * 尝试获取令牌
     */
    tryConsume(tokens: number = 1): boolean {
        this.refill();

        if (this.tokens >= tokens) {
            this.tokens -= tokens;
            return true;
        }

        return false;
    }

    /**
     * 等待获取令牌
     */
    async consume(tokens: number = 1): Promise<void> {
        this.refill();

        while (this.tokens < tokens) {
            const waitTime = (tokens - this.tokens) / this.refillRate;
            await new Promise(resolve => setTimeout(resolve, waitTime));
            this.refill();
        }

        this.tokens -= tokens;
    }

    /**
     * 补充令牌
     */
    private refill(): void {
        const now = Date.now();
        const elapsed = now - this.lastRefill;
        const newTokens = elapsed * this.refillRate;

        this.tokens = Math.min(this.capacity, this.tokens + newTokens);
        this.lastRefill = now;
    }

    /**
     * 获取当前令牌数
     */
    getAvailableTokens(): number {
        this.refill();
        return this.tokens;
    }
}

// 限流中间件（Express）
function rateLimitMiddleware(limiter: RateLimiter) {
    return (req: any, res: any, next: any) => {
        const key = req.ip || req.connection.remoteAddress;

        if (!limiter.check(key)) {
            const remaining = limiter.getRemaining(key);
            const resetTime = limiter.getResetTime(key);
            const retryAfter = Math.ceil((resetTime - Date.now()) / 1000);

            res.setHeader('X-RateLimit-Limit', limiter['maxRequests']);
            res.setHeader('X-RateLimit-Remaining', remaining);
            res.setHeader('X-RateLimit-Reset', Math.ceil(resetTime / 1000));

            return res.status(429).json({
                error: 'Too Many Requests',
                message: 'Rate limit exceeded',
                retryAfter
            });
        }

        const remaining = limiter.getRemaining(key);
        res.setHeader('X-RateLimit-Limit', limiter['maxRequests']);
        res.setHeader('X-RateLimit-Remaining', remaining);

        next();
    };
}

// 使用示例
const rateLimiter = new RateLimiter(60000, 100); // 每分钟100次
const tokenBucket = new TokenBucket(100, 0.1);   // 容量100，每10ms补充1个

app.use(rateLimitMiddleware(rateLimiter));

// 使用令牌桶限制特定操作
app.post('/api/upload', async (req, res) => {
    if (!tokenBucket.tryConsume(10)) {
        return res.status(429).json({ error: 'Upload rate limit exceeded' });
    }

    // 处理上传
});
```

---

## 2. 前端增强模式

### 2.1 防抖节流模式

**实现模板（Vue3）**：
```typescript
// composables/useDebounce.ts
import { ref, watch, onUnmounted } from 'vue';

export function useDebounce<T>(value: Ref<T>, delay: number = 300): Ref<T> {
    const debouncedValue = ref(value.value);
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    watch(value, (newValue) => {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }

        timeoutId = setTimeout(() => {
            debouncedValue.value = newValue;
            timeoutId = null;
        }, delay);
    });

    onUnmounted(() => {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
    });

    return debouncedValue;
}

// composables/useThrottle.ts
import { ref, watch, onUnmounted } from 'vue';

export function useThrottle<T>(value: Ref<T>, delay: number = 100): Ref<T> {
    const throttledValue = ref(value.value);
    let lastTime = 0;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    watch(value, (newValue) => {
        const now = Date.now();

        if (now - lastTime >= delay) {
            throttledValue.value = newValue;
            lastTime = now;
        } else {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }

            timeoutId = setTimeout(() => {
                throttledValue.value = newValue;
                lastTime = Date.now();
                timeoutId = null;
            }, delay - (now - lastTime));
        }
    });

    onUnmounted(() => {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
    });

    return throttledValue;
}

// 使用示例
<script setup lang="ts">
import { ref } from 'vue';
import { useDebounce, useThrottle } from '@/composables';

const searchTerm = ref('');
const debouncedSearch = useDebounce(searchTerm, 500);
const scrollPosition = useThrottle(ref(0), 100);

// 防抖搜索
watch(debouncedSearch, async (newTerm) => {
    if (newTerm) {
        const results = await searchAPI(newTerm);
        // 处理搜索结果
    }
});
</script>
```

---

### 2.2 乐观更新模式

**实现模板（Vue3 + Pinia）**：
```typescript
// stores/optimisticStore.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

interface UpdateOperation {
    id: string;
    revert: () => void;
    timestamp: number;
}

export const useOptimisticStore = defineStore('optimistic', () => {
    const pendingUpdates = ref<Map<string, UpdateOperation>>(new Map());

    /**
     * 乐观更新
     */
    async function optimisticUpdate<T>(
        id: string,
        optimisticValue: T,
        apiCall: () => Promise<T>,
        currentValue: T
    ): Promise<T> {
        const previousValue = currentValue;

        // 立即更新UI
        const updateOperation: UpdateOperation = {
            id,
            timestamp: Date.now(),
            revert: () => {
                // 恢复之前的值
                pendingUpdates.value.delete(id);
                // 触发更新通知
            }
        };

        pendingUpdates.value.set(id, updateOperation);

        try {
            // 调用API
            const result = await apiCall();

            // 成功，移除pending状态
            pendingUpdates.value.delete(id);

            return result;
        } catch (error) {
            // 失败，回滚UI
            updateOperation.revert();
            throw error;
        }
    }

    /**
     * 批量乐观更新
     */
    async function batchOptimisticUpdate<T>(
        operations: Array<{
            id: string;
            optimisticValue: T;
            apiCall: () => Promise<T>;
            currentValue: T;
        }>
    ): Promise<T[]> {
        const revertOperations: (() => void)[] = [];

        // 立即应用所有乐观更新
        operations.forEach(op => {
            const updateOperation: UpdateOperation = {
                id: op.id,
                timestamp: Date.now(),
                revert: () => {
                    pendingUpdates.value.delete(op.id);
                }
            };

            pendingUpdates.value.set(op.id, updateOperation);
            revertOperations.push(updateOperation.revert);
        });

        try {
            // 并行调用API
            const results = await Promise.all(
                operations.map(op => op.apiCall())
            );

            // 成功，移除所有pending状态
            operations.forEach(op => {
                pendingUpdates.value.delete(op.id);
            });

            return results;
        } catch (error) {
            // 失败，回滚所有更新
            revertOperations.forEach(revert => revert());
            throw error;
        }
    }

    return {
        pendingUpdates,
        optimisticUpdate,
        batchOptimisticUpdate
    };
});

// 使用示例
<script setup lang="ts">
import { ref } from 'vue';
import { useOptimisticStore } from '@/stores/optimistic';

const optimisticStore = useOptimisticStore();
const items = ref([
    { id: '1', name: 'Item 1', completed: false },
    { id: '2', name: 'Item 2', completed: false }
]);

async function toggleComplete(id: string) {
    const item = items.value.find(i => i.id === id);
    if (!item) return;

    const originalCompleted = item.completed;

    // 乐观更新UI
    item.completed = !item.completed;

    try {
        // 调用API
        await optimisticStore.optimisticUpdate(
            id,
            item,
            () => updateItemAPI(id, { completed: !originalCompleted }),
            item
        );
    } catch (error) {
        // 失败时UI会自动回滚
        console.error('Update failed:', error);
    }
}
</script>
```

---

### 2.3 请求重试模式

**实现模板（TypeScript）**：
```typescript
// utils/retry.ts
interface RetryOptions {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
    shouldRetry?: (error: any) => boolean;
    onRetry?: (attempt: number, error: any) => void;
}

export async function retry<T>(
    fn: () => Promise<T>,
    options: RetryOptions = {}
): Promise<T> {
    const {
        maxRetries = 3,
        baseDelay = 300,
        maxDelay = 30000,
        shouldRetry = defaultShouldRetry,
        onRetry
    } = options;

    let attempt = 0;
    let lastError: any;

    while (attempt <= maxRetries) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            attempt++;

            // 不应该重试或达到最大重试次数
            if (attempt > maxRetries || !shouldRetry(error, attempt)) {
                throw error;
            }

            // 计算延迟（指数退避）
            const delay = Math.min(
                baseDelay * Math.pow(2, attempt - 1),
                maxDelay
            );

            // 添加随机抖动
            const jitter = delay * 0.1 * Math.random();
            const finalDelay = delay + jitter;

            if (onRetry) {
                onRetry(attempt, error);
            }

            console.warn(
                `[Retry] Attempt ${attempt}/${maxRetries} failed, retrying in ${Math.round(finalDelay)}ms`,
                error
            );

            await new Promise(resolve => setTimeout(resolve, finalDelay));
        }
    }

    throw lastError;
}

/**
 * 默认重试条件
 */
function defaultShouldRetry(error: any, attempt: number): boolean {
    // 重试网络错误
    if (error.name === 'NetworkError' || error.code === 'ECONNRESET') {
        return true;
    }

    // 重试5xx错误
    if (error.response?.status >= 500) {
        return true;
    }

    // 重试429（Too Many Requests）
    if (error.response?.status === 429) {
        return true;
    }

    // 重试超时错误
    if (error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
        return true;
    }

    return false;
}

// 使用示例
async function fetchDataWithRetry() {
    return retry(
        () => fetch('/api/data').then(r => r.json()),
        {
            maxRetries: 5,
            baseDelay: 500,
            onRetry: (attempt, error) => {
                console.log(`Retrying (attempt ${attempt})...`);
            }
        }
    );
}
```

---

### 2.4 骨架屏模式

**实现模板（Vue3）**：
```vue
<!-- components/SkeletonLoader.vue -->
<template>
  <div class="skeleton-wrapper">
    <div v-if="loading" class="skeleton-container">
      <slot name="skeleton">
        <div class="skeleton-item" v-for="i in count" :key="i">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-content">
            <div class="skeleton-title"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text short"></div>
          </div>
        </div>
      </slot>
    </div>
    <slot v-else></slot>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  loading: boolean;
  count?: number;
}>();
</script>

<style scoped>
.skeleton-wrapper {
  min-height: 100px;
}

.skeleton-item {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-title {
  width: 60%;
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-text {
  width: 100%;
  height: 14px;
  border-radius: 4px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-text.short {
  width: 40%;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
```

---

### 2.5 错误边界模式

**实现模板（Vue3）**：
```vue
<!-- components/ErrorBoundary.vue -->
<template>
  <slot v-if="!error" />

  <div v-else class="error-boundary">
    <div class="error-icon">⚠️</div>
    <h3>出错了</h3>
    <p>{{ errorMessage }}</p>

    <div class="error-actions">
      <button @click="handleRetry" class="btn-retry">重试</button>
      <button @click="handleGoHome" class="btn-home">返回首页</button>
    </div>

    <details v-if="showDetails" class="error-details">
      <summary>错误详情</summary>
      <pre>{{ error.stack }}</pre>
    </details>
  </div>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured, type ErrorCaptured } from 'vue';

interface Props {
  fallback?: string;
  onError?: (error: Error, instance: any, info: string) => void;
  showDetails?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: false
});

const emit = defineEmits<{
  error: [error: Error, instance: any, info: string];
}>();

const error = ref<Error | null>(null);
const errorMessage = ref('');

onErrorCaptured((err: Error, instance, info): boolean => {
  error.value = err;
  errorMessage.value = props.fallback || err.message || '发生未知错误';

  // 上报错误
  if (props.onError) {
    props.onError(err, instance, info);
  }

  // 发送错误事件
  emit('error', err, instance, info);

  // 错误日志
  console.error('[ErrorBoundary]', err, info);

  // 阻止错误继续向上传播
  return false;
});

function handleRetry() {
  error.value = null;
}

function handleGoHome() {
  window.location.href = '/';
}
</script>

<style scoped>
.error-boundary {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 32px;
  text-align: center;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.error-boundary h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.error-boundary p {
  color: #666;
  margin-bottom: 24px;
}

.error-actions {
  display: flex;
  gap: 12px;
}

.btn-retry,
.btn-home {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-retry {
  background: #1890ff;
  color: white;
}

.btn-home {
  background: #f0f0f0;
  color: #333;
}

.error-details {
  margin-top: 24px;
  text-align: left;
  width: 100%;
  max-width: 600px;
}

.error-details summary {
  cursor: pointer;
  color: #666;
  margin-bottom: 8px;
}

.error-details pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}
</style>

// 使用示例
<template>
  <ErrorBoundary @error="handleGlobalError">
    <MyComponent />
  </ErrorBoundary>
</template>
```

---

## 3. 算法选择决策树

```
选择算法时的决策流程：

数据量 < 10
    ↓
简单遍历
    ↓
数据量 10-1000
    ↓
    ┌─ 搜索需求? ──是─→ 二分查找（需排序） / 线性查找
    │
    └─ 排序需求? ──是─→ 快速排序 / 归并排序
    │
    └─ 去重需求? ──是─→ Set / Map
    │
    └─ 频繁访问? ──是─→ Map / 缓存
    │
    └─ 满足基本需求

数据量 1000-10000
    ↓
    ┌─ 搜索需求? ──是─→ 二分查找 / 哈希表索引
    │
    └─ 排序需求? ──是─→ 归并排序（稳定）/ 快速排序
    │
    └─ 去重需求? ──是─→ 布隆过滤器（内存有限）
    │
    └─ 分页需求? ──是─→ 偏移分页 / 游标分页

数据量 > 10000
    ↓
    ┌─ 搜索需求? ──是─→ 布隆过滤器 + 数据库索引
    │
    └─ 排序需求? ──是─→ 数据库排序 / 外部排序
    │
    └─ 去重需求? ──是─→ 布隆过滤器（判断可能存在）
    │
    └─ 分页需求? ──是─→ 游标分页（推荐）
    │
    └─ 并发处理? ──是─→ Map聚合 / 批量查询
```

---

## 4. 性能优化最佳实践

### 后端优化清单

| 类别 | 优化项 | 实现方式 |
|------|--------|----------|
| 数据库 | 索引优化 | 为常用查询字段添加索引 |
| 数据库 | 批量操作 | 使用批量插入/更新代替单条 |
| 数据库 | N+1查询优化 | 使用JOIN或批量查询 |
| 数据库 | 连接池 | 配置适当的连接池大小 |
| 缓存 | 多级缓存 | L1(LRU) + L2(Redis) |
| 缓存 | 缓存预热 | 系统启动时预加载热点数据 |
| 缓存 | 缓存失效 | 数据变更时主动失效缓存 |
| 并发 | 异步处理 | 使用消息队列处理耗时任务 |
| 并发 | 连接复用 | HTTP/2、连接池 |
| 代码 | 算法优化 | 根据数据量选择合适算法 |

### 前端优化清单

| 类别 | 优化项 | 实现方式 |
|------|--------|----------|
| 加载 | 代码分割 | 动态import、路由懒加载 |
| 加载 | 资源压缩 | Gzip/Brotli压缩 |
| 加载 | 图片优化 | WebP格式、懒加载 |
| 渲染 | 虚拟滚动 | 长列表使用虚拟滚动 |
| 渲染 | 防抖节流 | 输入、滚动事件使用防抖节流 |
| 状态 | 本地缓存 | localStorage、IndexedDB |
| 状态 | 请求缓存 | SWR、React Query |
| 交互 | 骨架屏 | 加载时显示骨架屏 |
| 交互 | 乐观更新 | 提交后立即更新UI |

---

## 5. 缓存策略

### 缓存类型选择
| 缓存类型 | 适用场景 | 特点 |
|----------|----------|------|
| LRU缓存 | 进程内高频数据 | 快速，容量有限 |
| Redis | 分布式共享数据 | 可扩展，支持持久化 |
| 内存缓存 | 临时数据计算 | 超快，进程重启丢失 |
| 浏览器缓存 | 静态资源 | 减少网络请求 |
| CDN缓存 | 静态内容 | 全球加速 |

### 缓存失效策略
| 策略 | 适用场景 | 实现方式 |
|------|----------|----------|
| TTL失效 | 有时效性的数据 | 设置过期时间 |
| 主动失效 | 数据变更场景 | 更新时主动删除缓存 |
| 版本号 | 需要批量失效的场景 | 每次更新递增版本号 |
| 事件通知 | 分布式环境 | 使用发布订阅通知失效 |

---

## 7. AI代码增强模式

本文档提供了AI代码增强模式的详细实现模板和最佳实践，供技能执行时参考使用。

### 7.1 RAG（检索增强生成）增强

**适用场景**：文档问答、知识库检索、AI搜索

**核心增强**：
- **多路召回**：同时使用关键词检索和向量检索，合并结果提升召回率
- **重排序（Rerank）**：对召回结果进行二次排序，提升准确率
- **分块策略优化**：根据文档类型自适应分块（如代码按函数分块，文档按段落分块）
- **元数据过滤**：支持按元数据（如日期、分类）过滤检索结果

**RAG增强示例**：
```python
# 多路召回 + 重排序增强版
async def enhanced_rag_retrieval(query: str, filters: dict = None):
    # 路径1：向量检索
    vector_results = await vector_store.similarity_search(query, k=10, filters=filters)

    # 路径2：关键词检索
    keyword_results = await keyword_search(query, k=10, filters=filters)

    # 合并并去重
    merged_results = merge_and_dedupe(vector_results, keyword_results)

    # 重排序
    reranked = await rerank(query, merged_results, top_k=5)

    return reranked
```

### 7.2 Agent增强

**适用场景**：AI Agent、自主任务执行

**核心增强**：
- **工具调用重试**：工具调用失败时自动重试（最多3次）
- **并发工具调用**：支持并行调用无依赖关系的工具
- **工具执行超时**：设置工具执行超时时间，防止死锁
- **工具输出验证**：验证工具返回结果的格式和有效性

### 7.3 对话增强

**适用场景**：聊天机器人、对话管理

**核心增强**：
- **会话摘要**：长对话自动生成摘要，减少Token消耗
- **上下文压缩**：压缩历史消息，保留关键信息
- **敏感信息脱敏**：自动检测和脱敏敏感信息
- **多轮对话一致性**：维护上下文一致性，避免前后矛盾

### 7.4 AI服务通用增强

**适用场景**：所有AI相关服务

**核心增强**：
- **请求限流**：基于用户/IP的调用限流
- **Token计数**：实时记录Token消耗
- **成本追踪**：统计API调用成本
- **熔断降级**：AI服务不可用时降级到规则引擎或预设回复
- **响应缓存**：对相同问题的回答进行缓存，减少AI调用成本

---

## 6. 错误处理规范

### 缓存类型选择

| 缓存类型 | 适用场景 | 特点 |
|----------|----------|------|
| LRU缓存 | 进程内高频数据 | 快速，容量有限 |
| Redis | 分布式共享数据 | 可扩展，支持持久化 |
| 内存缓存 | 临时数据计算 | 超快，进程重启丢失 |
| 浏览器缓存 | 静态资源 | 减少网络请求 |
| CDN缓存 | 静态内容 | 全球加速 |

### 缓存失效策略

| 策略 | 适用场景 | 实现方式 |
|------|----------|----------|
| TTL失效 | 有时效性的数据 | 设置过期时间 |
| 主动失效 | 数据变更场景 | 更新时主动删除缓存 |
| 版本号 | 需要批量失效的场景 | 每次更新递增版本号 |
| 事件通知 | 分布式环境 | 使用发布订阅通知失效 |

---

## 6. 错误处理规范

### 错误码设计

| 错误码范围 | 含义 | 示例 |
|------------|------|------|
| 1000-1999 | 通用错误 | 1001: 参数错误 |
| 2000-2999 | 认证授权 | 2001: 未登录, 2002: 权限不足 |
| 3000-3999 | 业务错误 | 3001: 订单不存在, 3002: 库存不足 |
| 4000-4999 | 外部服务 | 4001: 支付失败, 4002: 短信发送失败 |
| 5000-5999 | 系统错误 | 5001: 数据库错误, 5002: 网络错误 |

### 统一错误处理

```typescript
// 统一错误响应格式
interface ErrorResponse {
    code: number;
    message: string;
    details?: any;
    timestamp: number;
    requestId?: string;
}

// 全局异常处理器
class GlobalErrorHandler {
    handle(error: any): ErrorResponse {
        if (error instanceof ValidationError) {
            return {
                code: 1001,
                message: '参数验证失败',
                details: error.details,
                timestamp: Date.now()
            };
        }

        if (error instanceof UnauthorizedError) {
            return {
                code: 2001,
                message: '未登录或登录已过期',
                timestamp: Date.now()
            };
        }

        // 默认错误
        return {
            code: 5000,
            message: error.message || '系统错误',
            timestamp: Date.now()
        };
    }
}
```
