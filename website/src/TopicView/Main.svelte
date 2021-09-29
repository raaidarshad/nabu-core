<script>
    import Topic from "./Topic.svelte";

    async function getTopics() {
        const res = await fetch(`./topics?limit=5`);
        const theJson = await res.json();

        if (res.ok) {
            return theJson;
        } else {
            throw new Error(theJson);
        }
    }

    let promise = getTopics();
</script>

<main>
    {#await promise}
        <p>Waiting...</p>
    {:then topics}
        {#each topics as topic}
            <Topic {topic}/>
        {/each}
    {/await}
</main>

<style>

</style>