import { fromAny } from "../helpers/protected/fromAny";
import axios from 'axios'
import fetchClient from "../helpers/fetchClient";
const Home = () => {
    const is_allowed = fromAny()
    console.log(is_allowed)
    if (is_allowed === true) {
        console.log("Success")
    }
    return (
        <div>
            Home Page
        </div>
    );
}
export default Home;