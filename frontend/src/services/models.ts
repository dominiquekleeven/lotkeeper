export interface ServerRealm {
    server: string;
    server_slug: string;
    realms: Realm[];
}

export interface Realm {
    realm: string;
    realm_slug: string;
}

export interface ServerRealmOption {
    server: string;
    server_slug: string;
    realm: string;
    realm_slug: string;
}

// Base models from auction.py
export interface Auction {
    item: Item;
    unit_buyout_price: number;
    unit_starting_bid_price: number;
    quantity: number;
}

export interface AuctionData {
    server: string;
    realm: string;
    auctions: Auction[];
}

export interface AuctionFilter {
    item_id?: number;
    item_name?: string;
    item_quality?: number;
    item_level?: number;
    item_class_index?: number;
    item_class_name?: string;
}

export interface ItemFilter {
    id?: number;
    name?: string;
    quality?: number;
    level?: number;
    class_index?: number;
    class_name?: string;
}

// Base models from item.py
export interface Item {
    id: number;
    name: string;
    link: string;
    icon: string;
    level: number;
    quality: number;
    max_stack_size: number;
    vendor_price: number;
    class_index: number;
    class_name: string;
}

// Base models from types.py
export interface PaginationFilter {
    limit: number;
    offset: number;
}

export interface PaginationInfo {
    limit: number;
    offset: number;
    total: number;
    current_page?: number;
    total_pages?: number;
    has_next?: boolean;
    has_previous?: boolean;
    next_offset?: number;
}

export interface PaginatedResponse<T> {
    data: T[];
    pagination: PaginationInfo;
}

// Base models from auction_datapoint.py
export interface AuctionPriceHourlySummary {
    timestamp: string; // ISO datetime string
    min_buyout_price: number;
    max_buyout_price: number;
    avg_buyout_price: number;
    median_buyout_price: number;
    p25_buyout_price: number;
    p75_buyout_price: number;
    p10_buyout_price: number;
    p90_buyout_price: number;
    outlier_count: number;
    datapoint_count: number;
}

export interface AuctionMarketActivityHourlySummary {
    timestamp: string; // ISO datetime string
    total_auctions: number;
    total_quantity: number;
    total_market_value: number;
    estimated_market_value: number;
    datapoint_count: number;
    outlier_count: number;
}

export interface AuctionRealmActivityHourlySummary {
    ts: string; // ISO datetime string
    total_auctions: number;
    total_quantity: number;
    total_market_value: number;
    estimated_market_value: number;
    datapoint_count: number;
    outlier_count: number;
}

// Search Query Models
export interface SearchQueryFilters {
    item_name?: string;
    item_id?: number;
    item_quality?: number;
    item_level?: number;
    item_class_index?: number;
    item_class_name?: string;
    server?: string;
    realm?: string;
    min_price?: number;
    max_price?: number;
    min_quantity?: number;
    max_quantity?: number;
}
