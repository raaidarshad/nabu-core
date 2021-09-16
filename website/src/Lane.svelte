<script>
    import Headline from "./Headline.svelte";
    export let title;
    export let bgcolor = "transparent";
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
    <p class="title">{title}</p>
    <div style="background-color: {bgcolor}; height: 100%;">
        <select bind:value={selected} on:change={handleChange}>
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
    </div>
</main>

<style>
    select {
        -webkit-appearance: none;
        -moz-appearance: none;
        background: transparent;
        background-image: url("data:image/svg+xml;utf8,<svg fill='black' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/><path d='M0 0h24v24H0z' fill='none'/></svg>");
        background-repeat: no-repeat;
        background-position-x: 100%;
        background-position-y: 5px;
        border: none;
        margin: 0;
        margin-top: 10px;
        padding-right: 20px;
        appearance: none;
        text-align: center;
        width: 100%;
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

    .title {
        margin: 0 auto;
        padding: 0 10px;
        color: #555555;
    }

    div {
        padding: 0 10px;
        border: 1px solid lightgrey;
    }

    main {
        height: 100%;
    }

    @media screen and (max-width: 650px) {
        .title {
            visibility: hidden;
        }
    }

</style>
