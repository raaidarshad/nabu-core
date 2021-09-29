<script>
    import Category from "./Category.svelte";
    export let topic;

    function filterToAllSidesBias(biases) {
        return topic.articles.filter(x => biases.includes(x.source.allsides_bias));
    }
</script>

<main>
    <div>Topic title</div>
    <div>
        <Category title={"Left"} articles={filterToAllSidesBias(["LEFT", "LEAN_LEFT"])} />
        <Category title={"Center"} articles={filterToAllSidesBias(["CENTER"])} />
        <Category title={"Right"} articles={filterToAllSidesBias(["RIGHT", "LEAN_RIGHT"])} />
    </div>
</main>

<style>

</style>