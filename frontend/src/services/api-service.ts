import { LOT_HOST } from '../common/constants';
import type {
    Auction,
    AuctionFilter,
    PaginatedResponse,
    AuctionPriceHourlySummary,
    AuctionMarketActivityHourlySummary,
    AuctionRealmActivityHourlySummary,
    ServerRealm,
    Item,
    ItemFilter
} from './models';

function buildHeaders(): Headers {
    return new Headers({
        'Content-Type': 'application/json'
    });
}

const API_V1_URL = LOT_HOST + '/api/v1';

export const API = {
    // Server Realms resource
    serverRealms: {
        async get(): Promise<ServerRealm[]> {
            const response = await fetch(API_V1_URL + '/server-realms', {
                method: 'GET',
                headers: buildHeaders()
            });
            if (!response.ok) {
                throw new Error(`Failed to get server realms: ${response.statusText}`);
            }
            return response.json();
        },
        async getBySlugs(server_slug: string, realm_slug: string): Promise<ServerRealm> {
            const response = await fetch(`${API_V1_URL}/server-realms/${server_slug}/${realm_slug}`, {
                method: 'GET',
                headers: buildHeaders()
            });
            if (!response.ok) {
                throw new Error(`Failed to get server realm: ${response.statusText}`);
            }
            return response.json();
        }
    },

    // Items resource
    items: {
        async getFiltered(
            server: string,
            realm: string,
            filter?: ItemFilter,
            limit: number = 50,
            offset: number = 0
        ): Promise<PaginatedResponse<Item>> {
            const params = new URLSearchParams();

            // Add pagination parameters
            params.append('limit', limit.toString());
            params.append('offset', offset.toString());

            // Add filter parameters if provided
            if (filter) {
                if (filter.id) params.append('id', filter.id.toString());
                if (filter.name) params.append('name', filter.name);
                if (filter.quality !== undefined) params.append('quality', filter.quality.toString());
                if (filter.level !== undefined) params.append('level', filter.level.toString());
                if (filter.class_index !== undefined) params.append('class_index', filter.class_index.toString());
                if (filter.class_name) params.append('class_name', filter.class_name);
            }

            const response = await fetch(`${API_V1_URL}/items/${server}/${realm}?${params.toString()}`, {
                method: 'GET',
                headers: buildHeaders()
            });
            if (!response.ok) {
                throw new Error(`Failed to get filtered items: ${response.statusText}`);
            }
            const data = await response.json();
            // Quick parsing, normalize names and deal with BKP \"Sparrow\" Smallbore
            data.data = data.data.map((item: Item) => {
                item.name = item.name.replace(/\\/g, '');
                return item;
            });
            return data;
        },

        async getBulk(server: string, realm: string): Promise<Item[]> {
            const response = await fetch(`${API_V1_URL}/items/${server}/${realm}/bulk`, {
                method: 'GET',
                headers: buildHeaders()
            });
            if (!response.ok) {
                throw new Error(`Failed to get bulk items: ${response.statusText}`);
            }
            return response.json();
        },

        async getCount(server: string, realm: string): Promise<number> {
            const response = await fetch(`${API_V1_URL}/items/${server}/${realm}/count`, {
                method: 'GET',
                headers: buildHeaders()
            });
            if (!response.ok) {
                throw new Error(`Failed to get items count: ${response.statusText}`);
            }
            return response.json();
        }
    },

    // Auctions resource
    auctions: {
        async getFiltered(
            server: string,
            realm: string,
            filter?: AuctionFilter,
            limit: number = 50,
            offset: number = 0
        ): Promise<PaginatedResponse<Auction>> {
            const params = new URLSearchParams();

            // Add pagination parameters
            params.append('limit', limit.toString());
            params.append('offset', offset.toString());

            // Add filter parameters if provided
            if (filter) {
                if (filter.item_id) params.append('item_id', filter.item_id.toString());
                if (filter.item_name) params.append('item_name', filter.item_name);
                if (filter.item_quality !== undefined) params.append('item_quality', filter.item_quality.toString());
                if (filter.item_level !== undefined) params.append('item_level', filter.item_level.toString());
                if (filter.item_class_index !== undefined) params.append('item_class_index', filter.item_class_index.toString());
                if (filter.item_class_name) params.append('item_class_name', filter.item_class_name);
            }

            const response = await fetch(`${API_V1_URL}/auctions/${server}/${realm}?${params.toString()}`, {
                method: 'GET',
                headers: buildHeaders()
            });
            if (!response.ok) {
                throw new Error(`Failed to get filtered auctions: ${response.statusText}`);
            }
            return response.json();
        },

        async getBulk(server: string, realm: string): Promise<Auction[]> {
            const response = await fetch(`${API_V1_URL}/auctions/${server}/${realm}/bulk`, {
                method: 'GET',
                headers: buildHeaders()
            });
            if (!response.ok) {
                throw new Error(`Failed to get bulk auctions: ${response.statusText}`);
            }
            return response.json();
        },

        async getCount(server: string, realm: string): Promise<number> {
            const response = await fetch(`${API_V1_URL}/auctions/${server}/${realm}/count`, {
                method: 'GET',
                headers: buildHeaders()
            });
            if (!response.ok) {
                throw new Error(`Failed to get auctions count: ${response.statusText}`);
            }
            return response.json();
        },

        async getValue(server: string, realm: string): Promise<number> {
            const response = await fetch(`${API_V1_URL}/auctions/${server}/${realm}/value`, {
                method: 'GET',
                headers: buildHeaders()
            });
            if (!response.ok) {
                throw new Error(`Failed to get auctions value: ${response.statusText}`);
            }
            return response.json();
        }
    },

    // Auction Datapoints resource
    auctionDatapoints: {
        async getPriceHourlySummary(
            server: string,
            realm: string,
            itemId: number,
            fromTimestamp?: number,
            toTimestamp?: number
        ): Promise<AuctionPriceHourlySummary[]> {
            const params = new URLSearchParams();
            if (fromTimestamp !== undefined) params.append('from_timestamp', fromTimestamp.toString());
            if (toTimestamp !== undefined) params.append('to_timestamp', toTimestamp.toString());

            const response = await fetch(
                `${API_V1_URL}/auctions/datapoints/${server}/${realm}/${itemId}/price-hourly-summary?${params.toString()}`,
                {
                    method: 'GET',
                    headers: buildHeaders()
                }
            );
            if (!response.ok) {
                throw new Error(`Failed to get price hourly summary: ${response.statusText}`);
            }
            return response.json();
        },

        async getItemActivityHourlySummary(
            server: string,
            realm: string,
            itemId: number,
            fromTimestamp?: number,
            toTimestamp?: number
        ): Promise<AuctionMarketActivityHourlySummary[]> {
            const params = new URLSearchParams();
            if (fromTimestamp !== undefined) params.append('from_timestamp', fromTimestamp.toString());
            if (toTimestamp !== undefined) params.append('to_timestamp', toTimestamp.toString());

            const response = await fetch(
                `${API_V1_URL}/auctions/datapoints/${server}/${realm}/${itemId}/activity-hourly-summary?${params.toString()}`,
                {
                    method: 'GET',
                    headers: buildHeaders()
                }
            );
            if (!response.ok) {
                throw new Error(`Failed to get item activity hourly summary: ${response.statusText}`);
            }
            return response.json();
        },
        async getRealmActivityHourlySummary(
            server: string,
            realm: string,
            fromTimestamp?: number,
            toTimestamp?: number
        ): Promise<AuctionRealmActivityHourlySummary[]> {
            const params = new URLSearchParams();
            if (fromTimestamp !== undefined) params.append('from_timestamp', fromTimestamp.toString());
            if (toTimestamp !== undefined) params.append('to_timestamp', toTimestamp.toString());

            const response = await fetch(
                `${API_V1_URL}/auctions/datapoints/${server}/${realm}/activity-hourly-summary?${params.toString()}`,
                {
                    method: 'GET',
                    headers: buildHeaders()
                }
            );
            if (!response.ok) {
                throw new Error(`Failed to get realm activity hourly summary: ${response.statusText}`);
            }
            return response.json();
        }
    }
};
