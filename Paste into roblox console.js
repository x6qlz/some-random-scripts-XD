
async function getPlayerInfo(playerId) {
    const userInfoUrl = `https://users.roblox.com/v1/users/${playerId}`;
    
    try {
        
        const userInfoResponse = await fetch(userInfoUrl);
        if (!userInfoResponse.ok) {
            throw new Error(`Error fetching user info: ${userInfoResponse.status}`);
        }
        const userInfo = await userInfoResponse.json();

        
        const playerInfo = `
**Username:** ${userInfo.name}
**Display Name:** ${userInfo.displayName}
**Description:** ${userInfo.description || "No description available"}
**Created:** ${new Date(userInfo.created).toLocaleDateString()}
**Account Age (days):** ${Math.floor((Date.now() - new Date(userInfo.created)) / (1000 * 60 * 60 * 24))}
**Is Verified:** ${userInfo.isVerified ? "Yes" : "No"}
**External Links:** ${userInfo.externalLinks && userInfo.externalLinks.length > 0 ? userInfo.externalLinks.join(', ') : "None"}
`;

        
        console.log(playerInfo);

    } catch (error) {
        console.error('Failed to fetch player info:', error);
    }
}


const playerId = prompt("Enter the Player ID:");
if (playerId) {
    getPlayerInfo(playerId);
}
