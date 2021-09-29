<script>
    import Article from "./Article.svelte";
    export let articles;
    export let title;
</script>

<main>
    <div>{title}</div>

    <div>
        <ul>
            {#each articles as article}
                <li>
                    <Article {article}/>
                </li>
            {/each}
        </ul>
    </div>
</main>

<style>

</style>