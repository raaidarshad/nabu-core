<script>
    import Headline from "./Headline.svelte";
    export let rssOptions;
    export let limit = 10;
    let selected = rssOptions[0];
    $: targetUrl = selected.url;

    async function getFeed(rssUrl) {
        const res = await fetch(`./feed?rssUrl=${rssUrl}&limit=${limit}`);
        const theJson = await res.json();

        if (res.ok) {
            return theJson;
        } else {
            throw new Error(theJson);
        }
    }

    async function handleChange() {}

    $: promise = getFeed(selected.url);
</script>

<main>
    <select bind:value={selected} on:change="{handleChange}">
		{#each rssOptions as rssOption}
			<option value={rssOption}>
				{rssOption.text}
			</option>
		{/each}
	</select>
    {#await promise}
        <p>Waiting...</p>
    {:then response}
        <ul>
            {#each response.entries as article}
                <li><Headline {article} /></li>
            {/each}
        </ul>
    {/await}
</main>

<style>
    select {
        background-color: transparent;
        border: none;
        margin: 0;
        width: 100%;
        text-align: center;
        margin-top: 10px;
        appearance: none;
    }

    select:hover {
        background-color: #dddddd55;
        cursor: pointer;
    }

    ul {
        list-style-type: none;
        list-style-position: outside;
        text-align: left;
        padding-left: 0;
        margin-top: 0;
    }
</style>
