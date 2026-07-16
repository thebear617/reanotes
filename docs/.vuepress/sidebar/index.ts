import { sidebar } from "vuepress-theme-hope";

import dlproject from "./dlproject.js";
import dlresearch from "./dlresearch.js";
import literature from "./literature.js";
import replearning from "./replearning.js";

export default sidebar({
  "/replearning/": replearning,
  "/dlproject/": dlproject,
  "/dlresearch/": dlresearch,
  "/literature/": literature,
});
