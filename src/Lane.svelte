<script>
    import Headline from "./Headline.svelte";
    export let rssUrl;
    export let limit = 10;

    async function getFeed() {
        const res = await fetch(`./feed?rssUrl=${rssUrl}&limit=${limit}`);
        const theJson = await res.json();

        if (res.ok) {
            return theJson;
        } else {
            throw new Error(theJson);
        }
    }

    let promise = getFeed();
</script>

<main>
    {#await promise}
        <p>Waiting...</p>
    {:then response}
        <h3>{response.feed.title}</h3>
        <ul>
            {#each response.entries as article}
                <li><Headline {article} /></li>
            {/each}
        </ul>
    {/await}
</main>

<style>
    main {
        max-width: 300px;
        margin: 0 auto;
    }

    h3 {
        text-align: center;
    }

    ul {
        list-style-type: none;
        list-style-position: outside;
        text-align: left;
        padding-left: 0;
    }
</style>
