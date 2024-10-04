
async function getGroupInfo(groupId) {
    const groupInfoUrl = `https://groups.roblox.com/v1/groups/${groupId}`;
    
    try {
        
        const groupInfoResponse = await fetch(groupInfoUrl);
        if (!groupInfoResponse.ok) {
            throw new Error(`Error fetching group info: ${groupInfoResponse.status}`);
        }
        const groupInfo = await groupInfoResponse.json();

        
        const groupDetails = `
**Group ID:** ${groupInfo.id || "N/A"}
**Group Name:** ${groupInfo.name || "No name available"}
**Description:** ${groupInfo.description || "No description available"}
**Member Count:** ${groupInfo.memberCount !== undefined ? groupInfo.memberCount : "N/A"}
**Owner:** ${groupInfo.owner ? groupInfo.owner.username || "No owner available" : "No owner available"}
**Publicity:** ${groupInfo.isPublic ? "Public" : "Private"}
`;

        
        console.log(groupDetails);

    } catch (error) {
        console.error('Failed to fetch group info:', error);
    }
}


const groupId = prompt("Enter the Group ID:");
if (groupId) {
    getGroupInfo(groupId);
}
