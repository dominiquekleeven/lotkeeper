export const LOT_HOST = (process.env.PUBLIC_LOT_HOST || '').replace(/\/$/, '');
export const SUPPORTED_SERVERS = ['project-epoch', 'turtle-wow', 'ascension'];

export const SERVER_ICONS = {
    'project-epoch': '/icons/project-epoch.webp',
    ascension: '/icons/ascension.webp',
    'turtle-wow': '/icons/turtle-wow.webp'
};

export const QUALITY_LEVELS = {
    0: 'Poor',
    1: 'Common',
    2: 'Uncommon',
    3: 'Rare',
    4: 'Epic',
    5: 'Legendary',
    6: 'Artifact',
    7: 'Heirloom'
};
