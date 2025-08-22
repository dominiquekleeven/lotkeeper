const ariaBusy = (busy: boolean) => {
    return busy ? 'true' : 'false';
};

const getIconUrl = (icon: string): string => {
    const iconFilename = (icon.split(/[\/\\]/).pop() || icon).toLowerCase();
    return `https://wow.zamimg.com/images/wow/icons/large/${iconFilename}.jpg`;
};

const getQualityColor = (quality: number): string => {
    return `quality-${quality}`;
};

const toSlug = (name: string): string => {
    return name
        .toLowerCase()
        .replace(/['"]/g, '') // Remove quotes and apostrophes
        .replace(/[^\w\s-]/g, '') // Remove special characters except word chars, spaces, and hyphens
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/-+/g, '-') // Replace multiple consecutive hyphens with single hyphen
        .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
};

const fromSlug = (slug: string): string => {
    return slug.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
};

// Formats copper to be like 12 <icon-gold> 20 <icon-silver> 10 <icon-copper>
const getFormattedPriceHtml = (price: number): string => {
    const gold = Math.floor(price / 10000);
    const silver = Math.floor((price % 10000) / 100);
    const copper = price % 100;

    const parts = [];
    if (gold > 0) parts.push(`${gold} <span class="icon-gold"></span>`);
    if (silver > 0) parts.push(`${silver} <span class="icon-silver"></span>`);
    if (copper > 0) parts.push(`${copper} <span class="icon-copper"></span>`);

    const content = parts.length > 0 ? parts.join(' ') : '0 <span class="icon-copper"></span>';
    return `<span class="price-display">${content}</span>`;
};

// Formats currency values for chart tooltips (e.g., "9s 80c" instead of "9.8")
const formatCurrencyForChart = (value: number, unit: 'gold' | 'silver' | 'copper'): string => {
    if (unit === 'gold') {
        const gold = Math.floor(value);
        const silver = Math.floor((value - gold) * 100);
        const copper = Math.floor(((value - gold) * 100 - silver) * 100);

        const parts = [];
        if (gold > 0) parts.push(`${gold}g`);
        if (silver > 0) parts.push(`${silver}s`);
        if (copper > 0) parts.push(`${copper}c`);

        return parts.length > 0 ? parts.join(' ') : '0c';
    } else if (unit === 'silver') {
        const silver = Math.floor(value);
        const copper = Math.floor((value - silver) * 100);

        const parts = [];
        if (silver > 0) parts.push(`${silver}s`);
        if (copper > 0) parts.push(`${copper}c`);

        return parts.length > 0 ? parts.join(' ') : '0c';
    } else {
        // copper unit
        return `${Math.floor(value)}c`;
    }
};

const formatRelativeTime = (timestamp: number | string | Date): string => {
    const now = new Date();
    const targetDate = new Date(timestamp);
    const diffInSeconds = Math.floor((now.getTime() - targetDate.getTime()) / 1000);

    if (diffInSeconds < 60) {
        return `${diffInSeconds} seconds ago`;
    }

    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
        return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
    }

    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
        return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
    }

    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 30) {
        return `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`;
    }

    const diffInMonths = Math.floor(diffInDays / 30);
    if (diffInMonths < 12) {
        return `${diffInMonths} month${diffInMonths !== 1 ? 's' : ''} ago`;
    }

    const diffInYears = Math.floor(diffInMonths / 12);
    return `${diffInYears} year${diffInYears !== 1 ? 's' : ''} ago`;
};

const getEpochTimestamp = (daysAgo?: number): number => {
    const now = Date.now();
    const offset = daysAgo ? daysAgo * 24 * 60 * 60 * 1000 : 0;
    return Math.floor((now - offset) / 1000);
};

const isAllianceRealm = (realm: string): boolean => {
    // Check whether the realm contains Alliance
    return realm.toLowerCase().includes('alliance');
};

const isHordeRealm = (realm: string): boolean => {
    // Check whether the realm contains Horde
    return realm.toLowerCase().includes('horde');
};

const isCrossFactionRealm = (realm: string): boolean => {
    // A realm without an alliance or horde suffix is a cross-faction realm
    return !isAllianceRealm(realm) && !isHordeRealm(realm);
};

export {
    ariaBusy,
    fromSlug,
    formatRelativeTime,
    getIconUrl,
    getQualityColor,
    getFormattedPriceHtml,
    formatCurrencyForChart,
    toSlug,
    getEpochTimestamp,
    isAllianceRealm,
    isHordeRealm,
    isCrossFactionRealm
};
